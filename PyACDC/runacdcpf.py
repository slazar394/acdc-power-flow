"""Runs a sequential AC/DC power flow.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import time
import numpy as np
from pypower.loadcase import loadcase
from pypower.runpf import runpf
from pypower.idx_bus import PQ, PV, REF, NONE, BUS_I, BUS_TYPE, PD, QD, GS, BS, \
    BUS_AREA, VM, VA, BASE_KV, ZONE, VMAX, VMIN
from pypower.idx_gen import GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, \
    PMAX, PMIN
from pypower.idx_brch import F_BUS, T_BUS, BR_STATUS, QT
from pypower.printpf import printpf

from loadcasedc import loadcasedc
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc
from idx_brchdc import idx_brchdc
from macdcoption import macdcoption
from convout import convout
from brchdcout import brchdcout
from brchout import brchout
from ext2intdc import ext2intdc
from ext2intac import ext2intac
from ext2intpu import ext2intpu
from makeYbusdc import makeYbusdc
from zonecheck import zonecheck
from dcnetworkpf import dcnetworkpf
from calclossac import calclossac
from calcslackdroop import calcslackdroop
from convlim import convlim
from convlimplot import convlimplot
from printdcpf import printdcpf
from int2extpu import int2extpu
from int2extdc import int2extdc
from int2extac import int2extac


def runacdcpf(caseac='case5_stagg', casedc='case5_stagg_MTDCslack',
              macdcopt=None, mpopt=None):
    """Runs a sequential AC/DC power flow.

    Args:
        caseac: AC power flow data (MATPOWER case struct/dict or filename)
        casedc: DC power flow data (MATACDC case struct/dict or filename)
        macdcopt: MATACDC options vector
        mpopt: MATPOWER options dict

    Returns:
        If nargout <= 2: (resultsac, resultsdc, converged, timecalc)
        If nargout > 2: (baseMVA, bus, gen, branch, busdc, convdc, branchdc,
                         converged, timecalc)
    """
    # Start time calculation
    start_time = time.time()

    # Default arguments
    if mpopt is None:
        from pypower.ppoption import ppoption
        mpopt = ppoption()
        mpopt['VERBOSE'] = 0  # No AC PF progress printed
        mpopt['OUT_ALL'] = 0  # No AC PF results printed

    if macdcopt is None:
        macdcopt = macdcoption()

    # Program options
    tolacdc = macdcopt[0]
    itmaxacdc = int(macdcopt[1])
    toldc = macdcopt[2]
    itmaxdc = int(macdcopt[3])
    tolslackdroop = macdcopt[4]
    itmaxslackdroop = int(macdcopt[5])
    tolslackdroopint = macdcopt[6]
    itmaxslackdroopint = int(macdcopt[7])
    multslack = int(macdcopt[8])
    limac = int(macdcopt[9])
    limdc = int(macdcopt[10])
    tollim = macdcopt[11]
    output = int(macdcopt[12])
    convplotopt = int(macdcopt[13])

    # Print options
    fd = 1

    # Initialize - load data
    ac_data = loadcase(caseac)
    baseMVA = ac_data['baseMVA']
    bus = ac_data['bus']
    gen = ac_data['gen']
    branch = ac_data['branch']
    dc_data = loadcasedc(casedc)
    baseMVAac = dc_data['baseMVAac']
    baseMVAdc = dc_data['baseMVAdc']
    pol = dc_data['pol']
    busdc = dc_data['busdc']
    convdc = dc_data['convdc']
    branchdc = dc_data['branchdc']

    # Define named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
        CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
        BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
        LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
        PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()

    F_BUSDC, T_BUSDC, BRDC_R, BRDC_L, BRDC_C, RATEDC_A, RATEDC_B, \
        RATEDC_C, BRDC_STATUS, PFDC, PTDC = idx_brchdc()

    # Data preparation
    # Converter outages
    busdc, conv0busi, conv1, conv1i, conv0, conv0i = convout(busdc, convdc)
    convdc = conv1

    # DC branch outages
    brchdc1, brchdc1i, brchdc0, brchdc0i = brchdcout(branchdc)
    branchdc = brchdc1

    # AC branch outages
    brch1, brch1i, brch0, brch0i = brchout(branch)
    branch = brch1

    # Generator outages
    gon = np.where(gen[:, GEN_STATUS] > 0)[0]
    goff = np.where(gen[:, GEN_STATUS] == 0)[0]
    gen0 = gen[goff, :].copy()
    gen = gen[gon, :].copy()

    # External to internal numbering
    i2edcpmt, i2edc, busdc, convdc, branchdc = ext2intdc(busdc, convdc, branchdc)
    i2eac, acdmbus, busdc, bus, gen, branch = ext2intac(busdc, bus, gen, branch)

    # Sort matrices by new bus numbers
    bus = bus[bus[:, BUS_I].argsort()]
    i2ebus = np.argsort(bus[:, BUS_I])
    gen = gen[gen[:, GEN_BUS].argsort()]
    i2egen = np.argsort(gen[:, GEN_BUS])
    branch = branch[branch[:, F_BUS].argsort()]
    i2ebrch = np.argsort(branch[:, F_BUS])
    busdc = busdc[busdc[:, BUSDC_I].argsort()]
    i2ebusdc = np.argsort(busdc[:, BUSDC_I])
    convdc = convdc[convdc[:, CONV_BUS].argsort()]
    i2econvdc = np.argsort(convdc[:, CONV_BUS])
    branchdc = branchdc[branchdc[:, F_BUSDC].argsort()]
    i2ebrchdc = np.argsort(branchdc[:, F_BUSDC])

    # Per unit conversion
    busdc, convdc, branchdc = ext2intpu(baseMVA, baseMVAac, baseMVAdc,
                                        busdc, convdc, branchdc)

    # Additional data preparation & index initialization
    convdc1 = np.zeros((busdc.shape[0], convdc.shape[1]))
    convdc1[convdc[:, CONV_BUS].astype(int) - 1, :] = convdc
    convdc = convdc1

    bdci = busdc[:, BUSAC_I].astype(int) - 1
    cdci = np.where(convdc[:, CONV_BUS] != 0)[0]
    slackdc = convdc[convdc[:, CONVTYPE_DC] == DCSLACK][:, CONV_BUS].astype(int) - 1
    droopdc = convdc[convdc[:, CONVTYPE_DC] == DCDROOP][:, CONV_BUS].astype(int) - 1
    ngriddc = int(np.max(busdc[:, GRIDDC]))

    # Violation check
    gridviol = np.setdiff1d(np.arange(1, ngriddc + 1),
                            busdc[np.concatenate([slackdc, droopdc]), GRIDDC])
    if len(gridviol) > 0:
        for grid in np.sort(gridviol):
            print(f'\n No slack or droop bus in dc grid {grid}.\n')
        raise ValueError('No droop controlled bus or slack bus defined for every dc grid!')

    # Remove multiple slack buses
    if multslack == 0:
        for ii in range(1, ngriddc + 1):
            slackdcii_mask = (busdc[:, GRIDDC] == ii) & (convdc[:, CONVTYPE_DC] == DCSLACK)
            slackdcii = np.where(slackdcii_mask)[0]
            if len(slackdcii) > 1:
                convdc[slackdcii[0], CONVTYPE_DC] = DCSLACK
                convdc[slackdcii[1:], CONVTYPE_DC] = DCNOSLACK
                slackdcii = slackdcii[0:1]
                print(f'\n Multiple dc slack busses defined in grid {ii}')
                print(f'\n     Bus {i2edc[slackdcii[0]]} kept as the slack bus')

        slackdc = np.where(convdc[:, CONVTYPE_DC] == DCSLACK)[0]

    slackdroopdc = np.union1d(slackdc, droopdc)
    noslackbdc = np.setdiff1d(np.arange(busdc.shape[0]), slackdc)

    # Remove converter and generator V control violations
    vcontrvsc = np.where(convdc[:, CONVTYPE_AC] == PVC)[0]
    vcontrgen = np.sort(np.concatenate([
        np.where(bus[:, BUS_TYPE] == PV)[0],
        np.where(bus[:, BUS_TYPE] == REF)[0]
    ]))
    vconfl = np.intersect1d(vcontrvsc, vcontrgen)
    convdc[vconfl, CONVTYPE_AC] = PQC
    convdc[vconfl, QCONV] = 0
    convdc[:, QCONV] = convdc[:, QCONV] * (convdc[:, CONVTYPE_AC] == PQC)

    if len(vconfl) > 0:
        print('\n Generator & VSC converter on the same bus')
        print(f'\n     Conflicting voltage control on bus {np.sort(i2eac[vconfl])}')
        print('\n => Corresponding VSC Converter set to PQ control without Q injections.')

    # Initialize AC network
    Vcref = convdc[:, VCONV]
    busVSC = bus.copy()
    gendm = np.zeros((0, gen.shape[1]))
    genPQ = np.array([], dtype=int)
    genPQi = np.array([], dtype=int)
    Qcmin_dum = -99999
    Qcmax_dum = 99999
    Pcmin_dum = 0
    Pcmax_dum = 99999

    # Dummy generator addition
    for ii in range(convdc.shape[0]):
        if bus[ii, BUS_TYPE] == PQ and convdc[ii, CONVTYPE_AC] == PVC:
            busVSC[ii, BUS_TYPE] = PV

            if ii + 1 not in gen[:, GEN_BUS]:
                new_gen = np.zeros((1, gen.shape[1]))
                new_gen[0, [GEN_BUS, PG, QG, QMAX, QMIN, VG, MBASE, GEN_STATUS, PMAX, PMIN]] = \
                    [ii + 1, 0, 0, Qcmax_dum, Qcmin_dum, Vcref[ii], baseMVAac, 1, Pcmax_dum, Pcmin_dum]
                gendm = np.vstack([gendm, new_gen]) if gendm.size else new_gen
            else:
                genPQ = np.append(genPQ, ii + 1)
                genPQii = np.where(gen[:, GEN_BUS] == ii + 1)[0]
                genPQi = np.append(genPQi, genPQii)

    gdmbus = gendm[:, GEN_BUS].astype(int) if gendm.size else np.array([], dtype=int)

    # Converter stations power injections
    Pvsc = convdc[:, PCONV] / baseMVA
    Qvsc = convdc[:, QCONV] / baseMVA

    # DC voltage droop setpoints
    PVdroop = np.zeros(busdc.shape[0])
    Pdcset = np.zeros(busdc.shape[0])
    Vdcset = np.zeros(busdc.shape[0])
    dVdcset = np.zeros(busdc.shape[0])

    PVdroop[cdci] = convdc[cdci, DROOP] * baseMVA
    Pdcset[cdci] = convdc[cdci, PDCSET] / baseMVA
    Vdcset[cdci] = convdc[cdci, VDCSET]
    dVdcset[cdci] = convdc[cdci, DVDCSET]

    # Voltage droop converter power initialization
    Pvsc[droopdc] = Pdcset[droopdc]

    # DC slack converter power injection initialization
    if len(slackdc) > 0:
        for ii in range(1, ngriddc + 1):
            slackdcii = np.where((busdc[:, GRIDDC] == ii) &
                                 (convdc[:, CONVTYPE_DC] == DCSLACK))[0]
            if len(slackdcii) > 0:
                Pvscii = Pvsc * (busdc[:, GRIDDC] == ii) * (convdc[:, CONVTYPE_DC] != DCSLACK)
                Pvsc[slackdcii] = -np.sum(Pvscii) / len(slackdcii)

    # Include converters as loads
    busVSC[cdci, PD] = bus[cdci, PD] - Pvsc[cdci] * baseMVA
    busVSC[cdci, QD] = bus[cdci, QD] - Qvsc[cdci] * baseMVA

    # Initialize converter quantities
    basekA = baseMVA / (np.sqrt(3) * convdc[:, BASEKVC])
    lossa = convdc[:, LOSSA] / baseMVA
    lossb = convdc[:, LOSSB] * (basekA / baseMVA)
    losscr = convdc[:, LOSSCR] * basekA ** 2 / baseMVA
    lossci = convdc[:, LOSSCI] * basekA ** 2 / baseMVA

    Rc = convdc[:, RCONV]
    Xc = convdc[:, XCONV]
    Zc = Rc + 1j * Xc

    Icmax = convdc[:, ICMAX]
    Vcmax = convdc[:, VCMAX]
    Vcmin = convdc[:, VCMIN]

    Bf = convdc[:, BF]

    Rtf = convdc[:, RTF]
    Xtf = convdc[:, XTF]
    Ztf = Rtf + 1j * Xtf

    # Initialize DC network quantities
    Ybusdc, Yfdc, Ytdc = makeYbusdc(busdc, branchdc)

    # Detect AC islands
    zonecheck(bus, gen, branch, i2eac, output)
    aczones = np.sort(np.unique(bus[:, ZONE]))

    # Main iteration loop
    Vdc = busdc[:, VDC].copy()
    genVSC = np.vstack([gen, gendm]) if gendm.size else gen.copy()
    gendmidx = np.where(~np.isin(genVSC[:, GEN_BUS], gen[:, GEN_BUS]))[0]
    Ps = Pvsc.copy()
    Pdc = np.zeros(busdc.shape[0])
    Ifdc = np.zeros(branchdc.shape[0])
    Pfdc = np.zeros(branchdc.shape[0])
    Ptdc = np.zeros(branchdc.shape[0])

    it = 0
    converged = False

    # Main loop
    while not converged and it <= itmaxacdc:
        it += 1

        Qs = Qvsc.copy()
        Ss = Ps + 1j * Qs

        # AC network power flow
        busVSCext = np.zeros((0, bus.shape[1]))
        genVSCext = np.zeros((0, gen.shape[1]))
        branchext = np.zeros((0, branch.shape[1]))

        for i in range(len(aczones)):
            buszi = np.where(bus[:, ZONE] == aczones[i])[0]
            genVSCzi = np.where(bus[genVSC[:, GEN_BUS].astype(int) - 1, ZONE] == aczones[i])[0]
            brchzi = np.where(bus[branch[:, F_BUS].astype(int) - 1, ZONE] == aczones[i])[0]

            busVSCz = busVSC[buszi, :].copy()
            genVSCz = genVSC[genVSCzi, :].copy()
            branchz = branch[brchzi, :].copy()

            if busVSCz.shape[0] > 1:
                accaseVSCz = {
                    'baseMVA': baseMVA,
                    'bus': busVSCz,
                    'gen': genVSCz,
                    'branch': branchz
                }
                results = runpf(accaseVSCz, mpopt)[0]
                baseMVA_result = results['baseMVA']
                busVSCz = results['bus']
                genVSCz = results['gen']
                branchz = results['branch']

            if busVSCext.size == 0:
                busVSCext = np.zeros((busVSC.shape[0], busVSCz.shape[1]))
                genVSCext = np.zeros((genVSC.shape[0], genVSCz.shape[1]))
                branchext = np.zeros((branch.shape[0], branchz.shape[1]))

            busVSCext[buszi, :] = busVSCz
            genVSCext[genVSCzi, :] = genVSCz
            branchext[brchzi, :] = branchz

        busVSC = busVSCext
        genVSC = genVSCext
        branch = branchext

        gendm = genVSC[gendmidx, :] if len(gendmidx) > 0 else np.zeros((0, gen.shape[1]))

        # Update grid side injection
        if len(gdmbus) > 0:
            Ss[gdmbus - 1] = Ss[gdmbus - 1] + 1j * gendm[:, QG] / baseMVA

        if len(genPQ) > 0:
            Ss[genPQ - 1] = Ss[genPQ - 1] + \
                            1j * (genVSC[genPQi, QG] - gen[genPQi, QG]) / baseMVA

        Ps = np.real(Ss)
        Qs = np.imag(Ss)

        genVSC[gendmidx, QG] = 0
        if len(genPQi) > 0:
            genVSC[genPQi, QG] = gen[genPQi, QG]

        # Converter calculations
        Vs = busVSC[bdci, VM] * np.exp(1j * busVSC[bdci, VA] * np.pi / 180)
        Itf = np.conj(Ss / Vs)
        Vf = Vs + Itf * Ztf
        Ssf = Vf * np.conj(Itf)
        Qf = -Bf * np.abs(Vf) ** 2
        Scf = Ssf + 1j * Qf
        Ic = np.conj(Scf / Vf)
        Vc = Vf + Ic * Zc
        Sc = Vc * np.conj(Ic)

        Pc = np.real(Sc)
        Qc = np.imag(Sc)
        Pcf = np.real(Scf)
        Qcf = np.imag(Scf)
        Psf = np.real(Ssf)
        Qsf = np.imag(Ssf)

        Ps_old = Ps.copy()

        if limac == 1:
            limviol = np.zeros(busdc.shape[0])
            SsL = np.zeros(busdc.shape[0], dtype=complex)
            plotarg = np.zeros((busdc.shape[0], 17), dtype=object)

            for ii in range(1, ngriddc + 1):
                cdcii_mask = busdc[:, GRIDDC] == ii
                cdcii = np.where(cdcii_mask & (convdc[:, CONV_BUS] != 0))[0]

                cdcslackii = np.intersect1d(cdcii, slackdc)
                if len(cdcslackii) > 0:
                    cdcii = np.setdiff1d(cdcii, cdcslackii)

                cdcii = cdcii[cdcii != 0]

                for jj in range(len(cdcii)):
                    cvjj = cdcii[jj]
                    limviol[cvjj], SsL[cvjj], plotarg[cvjj, :] = convlim(
                        Ss[cvjj], Vs[cvjj], Vc[cvjj], Ztf[cvjj],
                        Bf[cvjj], Zc[cvjj], Icmax[cvjj], Vcmax[cvjj],
                        Vcmin[cvjj], i2edc[cvjj], tollim, convplotopt
                    )

                limviolii = limviol * (busdc[:, GRIDDC] == ii)
                dSii = (SsL - Ss) * (busdc[:, GRIDDC] == ii) * \
                       (convdc[:, CONVTYPE_DC] != DCSLACK)

                if 2 in limviolii or 1 in limviolii:
                    if 2 in limviolii:
                        dSii = dSii * (limviolii == 2)
                        dSiimaxi = np.argmax(np.abs(np.real(dSii)))
                        print(f'\n  Active power setpoint of converter {i2edc[dSiimaxi]} '
                              f'changed from {np.real(Ss[dSiimaxi]) * baseMVA:.2f} MW to '
                              f'{np.real(SsL[dSiimaxi]) * baseMVA:.2f} MW.')
                        print(f'\n  Reactive power setpoint of converter {i2edc[dSiimaxi]} '
                              f'changed from {np.imag(Ss[dSiimaxi]) * baseMVA:.2f} MVAr to '
                              f'{np.imag(SsL[dSiimaxi]) * baseMVA:.2f} MVAr.\n')
                    else:
                        dSii = dSii * (limviolii == 1)
                        dSiimaxi = np.argmax(np.abs(np.imag(dSii)))
                        print(f'\n  Reactive power setpoint of converter {i2edc[dSiimaxi]} '
                              f'changed from {np.imag(Ss[dSiimaxi]) * baseMVA:.2f} MVAr to '
                              f'{np.imag(SsL[dSiimaxi]) * baseMVA:.2f} MVAr.\n')

                    if convplotopt != 0:
                        convlimplot(plotarg[dSiimaxi, :], i2edc[dSiimaxi])

                    Ss[dSiimaxi] = SsL[dSiimaxi]
                    Pvsc[dSiimaxi] = np.real(Ss[dSiimaxi])
                    Qvsc[dSiimaxi] = np.imag(Ss[dSiimaxi])
                    busVSC[dSiimaxi, PD] = bus[dSiimaxi, PD] - Pvsc[dSiimaxi] * baseMVA
                    busVSC[dSiimaxi, QD] = bus[dSiimaxi, QD] - Qvsc[dSiimaxi] * baseMVA
                else:
                    dSiimaxi = None

                if dSiimaxi is not None and convdc[dSiimaxi, CONVTYPE_AC] == PVC:
                    convdc[dSiimaxi, CONVTYPE_AC] = PQC
                    print(f'  Voltage control at converter bus {i2edc[dSiimaxi]} removed.\n')

                    busVSC[dSiimaxi, BUS_TYPE] = PQ

                    if dSiimaxi + 1 in gdmbus:
                        dSidx = np.where(gdmbus == dSiimaxi + 1)[0][0]
                        dSgenidx = gendmidx[dSidx]
                        gendm = np.delete(gendm, dSidx, axis=0)
                        genVSC = np.delete(genVSC, dSgenidx, axis=0)
                        gdmbus = np.delete(gdmbus, dSidx)
                        gendmidx = np.where(~np.isin(genVSC[:, GEN_BUS], gen[:, GEN_BUS]))[0]

                    if dSiimaxi + 1 in genPQ:
                        dSidx = np.where(genPQ == dSiimaxi + 1)[0][0]
                        genPQ = np.delete(genPQ, dSidx)
                        genPQi = np.delete(genPQi, dSidx)

                if dSiimaxi is not None and convdc[dSiimaxi, CONVTYPE_DC] == DCDROOP:
                    convdc[dSiimaxi, CONVTYPE_DC] = DCNOSLACK
                    droopdc = np.setdiff1d(droopdc, dSiimaxi)
                    slackdroopdc = np.setdiff1d(slackdroopdc, dSiimaxi)
                    print(f'  Droop control at converter bus {i2edc[dSiimaxi]} disabled.\n')

            # Recalculate after limit check
            Itf = np.conj(Ss / Vs)
            Vf = Vs + Itf * Ztf
            Ssf = Vf * np.conj(Itf)
            Qf = -Bf * np.abs(Vf) ** 2
            Scf = Ssf + 1j * Qf
            Ic = np.conj(Scf / Vf)
            Vc = Vf + Ic * Zc
            Sc = Vc * np.conj(Ic)

            Ps = np.real(Ss)
            Qs = np.imag(Ss)
            Pc = np.real(Sc)
            Qc = np.imag(Sc)
            Pcf = np.real(Scf)
            Qcf = np.imag(Scf)
            Psf = np.real(Ssf)
            Qsf = np.imag(Ssf)

        # Converter losses
        Ploss = calclossac(Pc, Qc, Vc, lossa, lossb, losscr, lossci)
        Pdc[cdci] = Pc[cdci] + Ploss[cdci]

        # DC networks power flow
        Vdc, Pdc = dcnetworkpf(Ybusdc, Vdc, Pdc, slackdc + 1, noslackbdc + 1,
                               droopdc + 1, PVdroop, Pdcset, Vdcset, dVdcset,
                               pol, toldc, itmaxdc)

        # DC line powers
        Ifdc = Yfdc @ Vdc
        Pfdc = pol * Vdc[branchdc[:, F_BUSDC].astype(int) - 1] * Ifdc
        Ptdc = pol * Vdc[branchdc[:, T_BUSDC].astype(int) - 1] * (-Ifdc)

        # Slack/droop bus loss calculation
        if len(slackdroopdc) > 0:
            Pc[slackdroopdc] = Pdc[slackdroopdc] - Ploss[slackdroopdc]

        itslack = 0
        convergedslackdroop = False

        while not convergedslackdroop and itslack <= itmaxslackdroop:
            itslack += 1
            Pcprev = Pc.copy()

            if len(slackdroopdc) > 0:
                Ps[slackdroopdc], Qc[slackdroopdc], Vc[slackdroopdc] = calcslackdroop(
                    Pc[slackdroopdc], Qs[slackdroopdc], Vs[slackdroopdc],
                    Vf[slackdroopdc], Vc[slackdroopdc], Ztf[slackdroopdc],
                    Bf[slackdroopdc], Zc[slackdroopdc], tolslackdroopint,
                    itmaxslackdroopint
                )

                Ploss[slackdroopdc] = calclossac(
                    Pc[slackdroopdc], Qc[slackdroopdc], Vc[slackdroopdc],
                    lossa[slackdroopdc], lossb[slackdroopdc],
                    losscr[slackdroopdc], lossci[slackdroopdc]
                )

                Pc[slackdroopdc] = Pdc[slackdroopdc] - Ploss[slackdroopdc]

            if len(slackdroopdc) > 0 and \
                    np.max(np.abs(Pcprev[slackdroopdc] - Pc[slackdroopdc])) < tolslackdroop:
                convergedslackdroop = True

        if not convergedslackdroop:
            print(f'\nSlackbus/Droop converter loss calculation did NOT converge '
                  f'in {itslack} iterations\n')

        busVSC[cdci, PD] = bus[cdci, PD] - Ps[cdci] * baseMVA

        if np.max(np.abs(Ps_old - Ps)) < tolacdc:
            converged = True

    # End of iteration
    timecalc = time.time() - start_time

    # Post processing
    if converged:
        if output:
            print(f'\nSequential solution method converged in {it} iterations\n')
    else:
        print(f'\nSequential solution method did NOT converge after {it} iterations\n')

    # Converter limit check
    if limac == 1:
        for ii in range(len(cdci)):
            cvii = cdci[ii]
            limviol, _, plotarg = convlim(
                Ss[cvii], Vs[cvii], Vc[cvii], Ztf[cvii],
                Bf[cvii], Zc[cvii], Icmax[cvii], Vcmax[cvii],
                Vcmin[cvii], i2edc[cvii], tollim, 1
            )
            if limviol != 0:
                if convdc[cvii, CONVTYPE_DC] == DCSLACK:
                    print(f'\n  Slackbus converter {i2edc[cvii]} is operating '
                          f'outside its limits.\n')
                elif convdc[cvii, CONVTYPE_DC] == DCNOSLACK:
                    print(f'\n  Converter {i2edc[cvii]} is operating outside its limits.\n')

            if convplotopt == 2:
                convlimplot(plotarg, i2edc[cvii])

    # Update matrices
    bus[:, VM] = busVSC[:, VM]
    bus[:, VA] = busVSC[:, VA]

    gen = genVSC[:gen.shape[0], :]

    busdc[:, PDC] = Pdc * baseMVA
    busdc[:, VDC] = Vdc

    convdc[:, PCONV] = Ps * baseMVA
    convdc[:, QCONV] = Qs * baseMVA
    convdc[:, VMC] = np.abs(Vc)
    convdc[:, VAC] = np.angle(Vc) * 180 / np.pi
    convdc[:, PCCONV] = Pc * baseMVA
    convdc[:, QCCONV] = Qc * baseMVA
    convdc[:, PCLOSS] = Ploss * baseMVA
    convdc[:, VMF] = np.abs(Vf)
    convdc[:, VAF] = np.angle(Vf) * 180 / np.pi
    convdc[:, PFIL] = Psf * baseMVA
    convdc[:, QCONVF] = Qsf * baseMVA
    convdc[:, QCCONVF] = Qcf * baseMVA

    branchdc[:, PFDC] = Pfdc * baseMVA
    branchdc[:, PTDC] = Ptdc * baseMVA

    # Internal to external conversion
    convdc = convdc[cdci, :]

    busdc, convdc, branchdc = int2extpu(baseMVA, baseMVAac, baseMVAdc,
                                        busdc, convdc, branchdc)

    # Undo sorting
    bus[i2ebus, :] = bus.copy()
    gen[i2egen, :] = gen.copy()
    branch[i2ebrch, :] = branch.copy()
    busdc[i2ebusdc, :] = busdc.copy()
    convdc[i2econvdc, :] = convdc.copy()
    branchdc[i2ebrchdc, :] = branchdc.copy()

    busdc, bus, gen, branch = int2extac(i2eac, acdmbus, busdc, bus, gen, branch)
    busdc, convdc, branchdc = int2extdc(i2edcpmt, i2edc, busdc, convdc, branchdc)

    # Generator outage inclusion
    gen1 = gen.copy()
    gen0[:, [PG, QG]] = 0
    gen = np.zeros((len(gon) + len(goff), gen1.shape[1]))
    gen[gon, :] = gen1
    gen[goff, :gen0.shape[1]] = gen0

    # Converter outages
    conv1 = convdc.copy()
    conv0 = np.column_stack([conv0, np.zeros((conv0.shape[0],
                                              conv1.shape[1] - conv0.shape[1]))])
    convdc = np.zeros((len(conv0i) + len(conv1i), conv1.shape[1]))
    convdc[conv0i, :] = conv0
    convdc[conv1i, :] = conv1

    if conv0busi.size > 0:
        busdc[conv0busi[:, 0].astype(int), BUSAC_I] = conv0busi[:, 1]

    # DC branch outages
    brchdc1 = branchdc.copy()
    brchdc0 = np.column_stack([brchdc0, np.zeros((brchdc0.shape[0],
                                                  brchdc1.shape[1] - brchdc0.shape[1]))])
    branchdc = np.zeros((len(brchdc0i) + len(brchdc1i), brchdc1.shape[1]))
    branchdc[brchdc0i, :] = brchdc0
    branchdc[brchdc1i, :] = brchdc1

    # AC branch outages
    if branch.shape[0] == 0:
        brch0 = np.column_stack([brch0, np.zeros((brch0.shape[0],
                                                  QT + 1 - brch0.shape[1]))])
        branch = brch0
    else:
        brch1 = branch.copy()
        brch0 = np.column_stack([brch0, np.zeros((brch0.shape[0],
                                                  brch1.shape[1] - brch0.shape[1]))])
        branch = np.zeros((len(brch0i) + len(brch1i), brch1.shape[1]))
        branch[brch0i, :] = brch0
        branch[brch1i, :] = brch1

    # Print results
    if output:
        printpf(baseMVA, bus, gen, branch, None, converged, timecalc)
        printdcpf(busdc, convdc, branchdc)

    # Output results
    resultsac = {
        'baseMVA': baseMVA,
        'bus': bus,
        'gen': gen,
        'branch': branch
    }

    resultsdc = {
        'baseMVAac': baseMVAac,
        'baseMVAdc': baseMVAdc,
        'pol': pol,
        'busdc': busdc,
        'convdc': convdc,
        'branchdc': branchdc
    }

    return resultsac, resultsdc, converged, timecalc


if __name__ == "__main__":
    print("Testing runacdcpf function:")

    resultsac, resultsdc, converged, timecalc = runacdcpf(
        'Cases/PowerFlowAC/case5_stagg',
        'Cases/PowerFlowDC/case5_stagg_MTDCslack'
    )

    print(f"\nConverged: {converged}")
    print(f"Time: {timecalc:.3f} seconds")
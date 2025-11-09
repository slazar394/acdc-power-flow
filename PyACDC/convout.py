"""Remove converters facing outages from converter matrix.

MatACDC - Copyright (C) 2012 Jef Beerten, KU Leuven
Converted from MATLAB to Python by Lazar Scekic
"""
import numpy as np
from idx_busdc import idx_busdc
from idx_convdc import idx_convdc


def convout(busdc, convdc):
    """Remove converters facing outages from converter matrix.

    The dc converter matrix is split into working (conv_operating) and non-working
    (conv_outage) converter matrices. The corresponding ac bus connection is
    removed from the busdc matrix.

    Args:
        busdc: dc bus matrix
        convdc: dc converter matrix

    Returns:
        tuple: (busdc, conv_outage_bus_info, conv_operating, conv_operating_indices,
                conv_outage, conv_outage_indices)
            busdc: updated dc bus matrix with ac buses of converters facing outages removed
            conv_outage_bus_info: 2 column matrix
                column 0: index of converter outages in converter matrix
                column 1: ac bus to which converter was connected before outage
            conv_operating: dc converter matrix with operating converters
            conv_operating_indices: indices of operating converters in original converter matrix
            conv_outage: dc converter matrix without operating converters
            conv_outage_indices: indices of converters with outages in original converter matrix
    """
    # Define named indices
    BUSDC_I, BUSAC_I, GRIDDC, PDC, VDC, BASE_KVDC, VDCMAX, VDCMIN, CDC = idx_busdc()

    DCDROOP, DCSLACK, DCNOSLACK, PVC, PQC, CONV_BUS, CONVTYPE_DC, \
        CONVTYPE_AC, PCONV, QCONV, VCONV, RTF, XTF, BF, RCONV, XCONV, \
        BASEKVC, VCMAX, VCMIN, ICMAX, CONVSTATUS, LOSSA, LOSSB, LOSSCR, \
        LOSSCI, DROOP, PDCSET, VDCSET, DVDCSET, VMC, VAC, PCCONV, QCCONV, \
        PCLOSS, VMF, VAF, PFIL, QCONVF, QCCONVF = idx_convdc()

    # Converter status validity check
    status_vals = convdc[:, CONVSTATUS]
    if np.any((status_vals != 0) & (status_vals != 1)):
        raise ValueError('Converter status flags must be either 0 or 1')

    # Find converter indices
    conv_outage_indices = np.where(convdc[:, CONVSTATUS] == 0)[0]
    conv_operating_indices = np.where(convdc[:, CONVSTATUS] == 1)[0]

    # Define converter outage and operating matrices
    conv_outage = convdc[conv_outage_indices, :].copy()
    conv_operating = convdc[conv_operating_indices, :].copy()

    # Reset converter powers and voltages for outages
    conv_outage[:, PCONV] = 0
    conv_outage[:, QCONV] = 0

    # Remove ac bus of converter with outage in busdc matrix
    conv_outage_bus_info = []

    if len(conv_outage_indices) > 0:
        for i in range(len(conv_outage_indices)):
            found = False
            for j in range(busdc.shape[0]):
                # Check for same dc bus number
                if conv_outage[i, CONV_BUS] == busdc[j, BUSDC_I]:
                    conv_outage_bus_info.append([j, busdc[j, BUSAC_I]])
                    busdc[j, BUSAC_I] = 0
                    found = True
                    break

    # Convert to numpy array if not empty
    if conv_outage_bus_info:
        conv_outage_bus_info = np.array(conv_outage_bus_info)
    else:
        conv_outage_bus_info = np.array([]).reshape(0, 2)

    return busdc, conv_outage_bus_info, conv_operating, conv_operating_indices, \
        conv_outage, conv_outage_indices


if __name__ == "__main__":
    from Cases.PowerFlowDC.case5_stagg_MTDCslack import case5_stagg_MTDCslack

    print("Testing convout function:")

    # Load test case
    baseMVAac, baseMVAdc, pol, busdc, convdc, branchdc = case5_stagg_MTDCslack()

    print(f"\nOriginal converter matrix shape: {convdc.shape}")
    print(f"Original busdc matrix shape: {busdc.shape}")
    print(f"All converters status: {convdc[:, 15]}")  # CONVSTATUS is at index 15

    # Simulate an outage on converter 2
    convdc_test = convdc.copy()
    convdc_test[1, 15] = 0  # Set second converter to outage status

    print(f"\nAfter setting converter 2 to outage status: {convdc_test[:, 15]}")

    # Test convout
    busdc_out, conv_outage_bus_info, conv_operating, conv_operating_indices, \
        conv_outage, conv_outage_indices = convout(busdc.copy(), convdc_test)

    print(f"\nResults:")
    print(f"Number of operating converters: {len(conv_operating_indices)}")
    print(f"Operating converter indices: {conv_operating_indices}")
    print(f"Number of outage converters: {len(conv_outage_indices)}")
    print(f"Outage converter indices: {conv_outage_indices}")
    print(f"Outage bus info shape: {conv_outage_bus_info.shape}")
    if conv_outage_bus_info.size > 0:
        print(f"Outage bus info:\n{conv_outage_bus_info}")
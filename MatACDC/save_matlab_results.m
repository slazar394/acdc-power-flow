function save_matlab_results

% SAVE_MATLAB_RESULTS  Run tests and save results for comparison with Python
%
% This script runs the same test cases as test_acdcpf.m but saves the
% results in a .mat file that can be loaded by Python for comparison.

%   MatACDC
%   Copyright (C) 2012 Jef Beerten
%   University of Leuven (KU Leuven)
%   Converted for comparison by Lazar Scekic

%% define options
mdopt = macdcoption;
mdopt(13) = 0;     % no output info

%% Initialize results structure
matlab_results = struct();

%% Test 1: voltage slack control
fprintf('> Test 1: Voltage slack control\n')
try
    [baseMVA, bus, gen, branch, busdc, convdc, branchdc, converged, timecalc] = ...
        runacdcpf('case5_stagg', 'case5_stagg_MTDCslack', mdopt);
    
    matlab_results.test1_slack.resultsac.baseMVA = baseMVA;
    matlab_results.test1_slack.resultsac.bus = bus;
    matlab_results.test1_slack.resultsac.gen = gen;
    matlab_results.test1_slack.resultsac.branch = branch;
    
    matlab_results.test1_slack.resultsdc.busdc = busdc;
    matlab_results.test1_slack.resultsdc.convdc = convdc;
    matlab_results.test1_slack.resultsdc.branchdc = branchdc;
    
    matlab_results.test1_slack.converged = converged;
    matlab_results.test1_slack.timecalc = timecalc;
    matlab_results.test1_slack.case_ac = 'case5_stagg';
    matlab_results.test1_slack.case_dc = 'case5_stagg_MTDCslack';
    
    fprintf('   -> Done. Converged: %d, Time: %.4fs\n', converged, timecalc);
catch ME
    fprintf('   -> FAILED: %s\n', ME.message);
    matlab_results.test1_slack.error = ME.message;
end

%% Test 2: voltage droop control
fprintf('> Test 2: Voltage droop control\n')
try
    [baseMVA, bus, gen, branch, busdc, convdc, branchdc, converged, timecalc] = ...
        runacdcpf('case5_stagg', 'case5_stagg_MTDCdroop', mdopt);
    
    matlab_results.test2_droop.resultsac.baseMVA = baseMVA;
    matlab_results.test2_droop.resultsac.bus = bus;
    matlab_results.test2_droop.resultsac.gen = gen;
    matlab_results.test2_droop.resultsac.branch = branch;
    
    matlab_results.test2_droop.resultsdc.busdc = busdc;
    matlab_results.test2_droop.resultsdc.convdc = convdc;
    matlab_results.test2_droop.resultsdc.branchdc = branchdc;
    
    matlab_results.test2_droop.converged = converged;
    matlab_results.test2_droop.timecalc = timecalc;
    matlab_results.test2_droop.case_ac = 'case5_stagg';
    matlab_results.test2_droop.case_dc = 'case5_stagg_MTDCdroop';
    
    fprintf('   -> Done. Converged: %d, Time: %.4fs\n', converged, timecalc);
catch ME
    fprintf('   -> FAILED: %s\n', ME.message);
    matlab_results.test2_droop.error = ME.message;
end

%% Test 3: infinite grid
fprintf('> Test 3: Infinite grid\n')
try
    [baseMVA, bus, gen, branch, busdc, convdc, branchdc, converged, timecalc] = ...
        runacdcpf('case3_inf', 'case5_stagg_MTDCdroop', mdopt);
    
    matlab_results.test3_inf.resultsac.baseMVA = baseMVA;
    matlab_results.test3_inf.resultsac.bus = bus;
    matlab_results.test3_inf.resultsac.gen = gen;
    matlab_results.test3_inf.resultsac.branch = branch;
    
    matlab_results.test3_inf.resultsdc.busdc = busdc;
    matlab_results.test3_inf.resultsdc.convdc = convdc;
    matlab_results.test3_inf.resultsdc.branchdc = branchdc;
    
    matlab_results.test3_inf.converged = converged;
    matlab_results.test3_inf.timecalc = timecalc;
    matlab_results.test3_inf.case_ac = 'case3_inf';
    matlab_results.test3_inf.case_dc = 'case5_stagg_MTDCdroop';
    
    fprintf('   -> Done. Converged: %d, Time: %.4fs\n', converged, timecalc);
catch ME
    fprintf('   -> FAILED: %s\n', ME.message);
    matlab_results.test3_inf.error = ME.message;
end

%% Test 4: multiple ac and dc systems
fprintf('> Test 4: Multiple AC and DC systems\n')
try
    [baseMVA, bus, gen, branch, busdc, convdc, branchdc, converged, timecalc] = ...
        runacdcpf('case24_ieee_rts1996_3zones', 'case24_ieee_rts1996_MTDC', mdopt);
    
    matlab_results.test4_multi.resultsac.baseMVA = baseMVA;
    matlab_results.test4_multi.resultsac.bus = bus;
    matlab_results.test4_multi.resultsac.gen = gen;
    matlab_results.test4_multi.resultsac.branch = branch;
    
    matlab_results.test4_multi.resultsdc.busdc = busdc;
    matlab_results.test4_multi.resultsdc.convdc = convdc;
    matlab_results.test4_multi.resultsdc.branchdc = branchdc;
    
    matlab_results.test4_multi.converged = converged;
    matlab_results.test4_multi.timecalc = timecalc;
    matlab_results.test4_multi.case_ac = 'case24_ieee_rts1996_3zones';
    matlab_results.test4_multi.case_dc = 'case24_ieee_rts1996_MTDC';
    
    fprintf('   -> Done. Converged: %d, Time: %.4fs\n', converged, timecalc);
catch ME
    fprintf('   -> FAILED: %s\n', ME.message);
    matlab_results.test4_multi.error = ME.message;
end

%% Save results
output_file = 'matlab_results.mat';
save(output_file, '-struct', 'matlab_results');
fprintf('\n=================================================================\n');
fprintf('Results saved to: %s\n', output_file);
fprintf('=================================================================\n');

%% Print summary
fprintf('\nSummary:\n');
tests = fieldnames(matlab_results);
for i = 1:length(tests)
    test_name = tests{i};
    test_data = matlab_results.(test_name);
    
    if isfield(test_data, 'error')
        fprintf('  %s: FAILED\n', test_name);
    elseif isfield(test_data, 'converged')
        if test_data.converged
            fprintf('  %s: PASS\n', test_name);
        else
            fprintf('  %s: NO CONVERGENCE\n', test_name);
        end
    else
        fprintf('  %s: UNKNOWN\n', test_name);
    end
end

return;

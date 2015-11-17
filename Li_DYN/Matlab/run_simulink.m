%% simulation parameters
model_name = 'raven2_model';
StopTime = sim_time;
open(model_name);
set_param(model_name,'IgnoredZcDiagnostic','none');
set_param(model_name,'MaskedZcDiagnostic','none');
set_param(model_name,'StopTime',num2str(StopTime));
fprintf(' done!\n');
fprintf(' simulating ''raven2_model.slx'' ...');
sim(model_name);
fprintf(' finished!\n');

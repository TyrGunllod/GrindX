param(
    [string]$GrindxPackages = "D:\\_Projetos\\GrindX\\packages",
    [switch]$Verbose
)
$env:GRINDX_PACKAGES = $GrindxPackages
$pytestArgs = @("-v")
if ($Verbose) { $pytestArgs += "--tb=long" } else { $pytestArgs += "--tb=short" }
python -m pytest "app/modules/{module_name}/tests/" @pytestArgs

$ErrorActionPreference = 'Stop'

$backendPath = Resolve-Path '.\backend'
$sqlPath = Resolve-Path '.\docs'
$migrations = @(
    @{ App = 'authentication'; Migration = '0002_alter_user_options' },
    @{ App = 'etl'; Migration = '0001_initial' },
    @{ App = 'analytics'; Migration = '0001_initial' },
    @{ App = 'ml'; Migration = '0001_initial' },
    @{ App = 'dashboard'; Migration = '0001_initial' },
    @{ App = 'reports'; Migration = '0001_initial' }
)

Push-Location $backendPath
try {
    foreach ($item in $migrations) {
        $output = Join-Path $sqlPath "$($item.App)_$($item.Migration).sql"
        python manage.py sqlmigrate $item.App $item.Migration | Out-File -FilePath $output -Encoding utf8
        Write-Host "Generado: $output"
    }
}
finally {
    Pop-Location
}

$folder1 = "D:\repros\agentic-shared\.github\agents"
$folder2 = "D:\repros\Agentic-Coding\.github\agents"

Get-ChildItem $folder1 -File -Recurse | ForEach-Object {
    $relativePath = $_.FullName.Substring($folder1.Length)
    $file2 = Join-Path $folder2 $relativePath

    if (Test-Path $file2) {
        $diff = Compare-Object `
            (Get-Content $_.FullName) `
            (Get-Content $file2)

        if ($diff) {
            Write-Host "`nDifferences found in $relativePath"
            $diff
        }
    }
}
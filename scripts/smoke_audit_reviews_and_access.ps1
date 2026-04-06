param(
    [string]$ApiDir = '.codex_build\accesslog_auditing_api',
    [string]$WorkflowDir = '.codex_build\accesslog_workflows_server',
    [string]$IdentityDir = '.codex_build\accesslog_identity_api',
    [string]$ApiBaseUrl = 'http://localhost:5023',
    [string]$WorkflowBaseUrl = 'http://localhost:5000',
    [string]$IdentityBaseUrl = 'http://localhost:5239'
)

$ErrorActionPreference = 'Stop'

function Invoke-JsonRequest {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers = @{},
        $Body = $null,
        [string]$ContentType = 'application/json'
    )

    $params = @{
        Method = $Method
        Uri = $Uri
        Headers = $Headers
        UseBasicParsing = $true
        ErrorAction = 'Stop'
    }

    if ($null -ne $Body) {
        if ($Body -is [string]) {
            $params.Body = $Body
        } else {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        $params.ContentType = $ContentType
    }

    $response = Invoke-WebRequest @params
    if ([string]::IsNullOrWhiteSpace($response.Content)) {
        return $null
    }

    return $response.Content | ConvertFrom-Json
}

function Invoke-FormCurl {
    param(
        [string]$Uri,
        [string[]]$HeaderLines,
        [string[]]$FormLines,
        [string]$OutFile = ''
    )

    $args = @('-sS', '-w', 'HTTPSTATUS:%{http_code}', '-X', 'POST', $Uri)
    foreach ($header in $HeaderLines) {
        $args += @('-H', $header)
    }
    foreach ($form in $FormLines) {
        $args += @('-F', $form)
    }
    if (-not [string]::IsNullOrWhiteSpace($OutFile)) {
        $args += @('-o', $OutFile)
    }

    $output = & curl.exe @args
    $text = [string]::Join('', $output)
    $marker = 'HTTPSTATUS:'
    $idx = $text.LastIndexOf($marker)
    if ($idx -lt 0) {
        throw "Could not parse curl response for ${Uri}: $text"
    }

    $body = $text.Substring(0, $idx)
    $status = [int]$text.Substring($idx + $marker.Length)
    return [pscustomobject]@{
        StatusCode = $status
        Body = $body
    }
}

function Add-Result {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $script:results.Add([pscustomobject]@{
        Test = $Name
        Passed = $Passed
        Detail = $Detail
    }) | Out-Null
}

function Get-ObjectList {
    param(
        $Object,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        $property = $Object.PSObject.Properties[$name]
        if ($property) {
            return @($property.Value)
        }
    }

    return @()
}

function Invoke-SqlScalar {
    param(
        [string]$ConnectionString,
        [string]$Sql
    )

    $payload = @{
        connection_string = $ConnectionString
        sql = $Sql
        mode = 'scalar'
    } | ConvertTo-Json -Compress

    $result = $payload | python -c "import json, sys, psycopg2; payload=json.load(sys.stdin); conn=psycopg2.connect(payload['connection_string']); cur=conn.cursor(); cur.execute(payload['sql']); row=cur.fetchone(); print(json.dumps(row[0] if row else None)); conn.close()"
    return $result | ConvertFrom-Json
}

function Invoke-SqlRow {
    param(
        [string]$ConnectionString,
        [string]$Sql
    )

    $payload = @{
        connection_string = $ConnectionString
        sql = $Sql
        mode = 'row'
    } | ConvertTo-Json -Compress

    $result = $payload | python -c "import json, sys, psycopg2, psycopg2.extras; payload=json.load(sys.stdin); conn=psycopg2.connect(payload['connection_string']); cur=conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor); cur.execute(payload['sql']); row=cur.fetchone(); print(json.dumps(row, default=str)); conn.close()"
    if ([string]::IsNullOrWhiteSpace($result) -or $result -eq 'null') {
        return $null
    }
    return $result | ConvertFrom-Json
}

$workspace = (Resolve-Path '.').Path
$results = New-Object System.Collections.Generic.List[object]
$logDir = Join-Path $workspace '.codex_build'
$docPath = Join-Path $workspace '.codex_tmp\smoke-review-doc.txt'
$downloadPath = Join-Path $workspace '.codex_tmp\smoke-review-download.bin'
$resultsPath = Join-Path $workspace '.codex_tmp\smoke_review_and_access_results.txt'

$headers = @{
    'X-Audit-User-Id' = '1'
    'X-Audit-User-Role' = 'admin'
    'X-Audit-User-Name' = 'System Administrator'
}
$curlHeaders = @(
    'X-Audit-User-Id: 1',
    'X-Audit-User-Role: admin',
    'X-Audit-User-Name: System Administrator'
)

$apiExe = Join-Path $workspace $ApiDir | Join-Path -ChildPath 'Affine.Auditing.API.exe'
$workflowExe = Join-Path $workspace $WorkflowDir | Join-Path -ChildPath 'Affine.Auditing.Workflows.Server.exe'
$identityExe = Join-Path $workspace $IdentityDir | Join-Path -ChildPath 'Affina.Identity.API.exe'
$apiWorkingDir = Split-Path $apiExe -Parent
$workflowWorkingDir = Split-Path $workflowExe -Parent
$identityWorkingDir = Split-Path $identityExe -Parent
$connectionString = 'postgresql://postgres:Monday%40123@localhost:5432/Risk_Assess_Framework'

Set-Content -Path $docPath -Value 'smoke review and access log document'

$wfProc = $null
$apiProc = $null
$identityProc = $null
$tempRef = $null

try {
    $env:ASPNETCORE_URLS = $WorkflowBaseUrl
    $env:ASPNETCORE_ENVIRONMENT = 'Development'
    $env:Http__BaseUrl = $WorkflowBaseUrl
    $env:Http__BasePath = '/elsa/api'
    $wfProc = Start-Process -FilePath $workflowExe `
        -WorkingDirectory $workflowWorkingDir `
        -RedirectStandardOutput (Join-Path $logDir 'review_access_wf.out.log') `
        -RedirectStandardError (Join-Path $logDir 'review_access_wf.err.log') `
        -WindowStyle Hidden `
        -PassThru

    $env:ASPNETCORE_URLS = $ApiBaseUrl
    $env:ASPNETCORE_ENVIRONMENT = 'Development'
    $env:WorkflowServiceUrl = $WorkflowBaseUrl
    $env:WorkflowServiceApiKey = '00000000-0000-0000-0000-000000000000'
    $apiProc = Start-Process -FilePath $apiExe `
        -WorkingDirectory $apiWorkingDir `
        -RedirectStandardOutput (Join-Path $logDir 'review_access_api.out.log') `
        -RedirectStandardError (Join-Path $logDir 'review_access_api.err.log') `
        -WindowStyle Hidden `
        -PassThru

    $env:ASPNETCORE_URLS = $IdentityBaseUrl
    $env:ASPNETCORE_ENVIRONMENT = 'Development'
    $identityProc = Start-Process -FilePath $identityExe `
        -WorkingDirectory $identityWorkingDir `
        -RedirectStandardOutput (Join-Path $logDir 'review_access_identity.out.log') `
        -RedirectStandardError (Join-Path $logDir 'review_access_identity.err.log') `
        -WindowStyle Hidden `
        -PassThru

    $wfReady = $false
    $apiReady = $false
    $identityReady = $false

    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Milliseconds 800

        if (-not $wfReady) {
            try {
                $wf = Invoke-WebRequest -Uri "$WorkflowBaseUrl/elsa/api/workflow-definitions" `
                    -Headers @{ Authorization = 'ApiKey 00000000-0000-0000-0000-000000000000' } `
                    -UseBasicParsing `
                    -ErrorAction Stop
                if ($wf.StatusCode -eq 200) {
                    $wfReady = $true
                }
            }
            catch {
            }
        }

        if (-not $apiReady) {
            try {
                $api = Invoke-WebRequest -Uri "$ApiBaseUrl/api/v1/AuditPlatform/GetClientConfiguration" `
                    -Headers $headers `
                    -UseBasicParsing `
                    -ErrorAction Stop
                if ($api.StatusCode -eq 200) {
                    $apiReady = $true
                }
            }
            catch {
            }
        }

        if (-not $identityReady) {
            try {
                $identity = Invoke-WebRequest -Uri "$IdentityBaseUrl/swagger/index.html" `
                    -UseBasicParsing `
                    -ErrorAction Stop
                if ($identity.StatusCode -eq 200) {
                    $identityReady = $true
                }
            }
            catch {
            }
        }

        if ($wfReady -and $apiReady -and $identityReady) {
            break
        }
    }

    Add-Result 'Workflow server startup' $wfReady $(if ($wfReady) { 'HTTP 200' } else { 'did not become ready' })
    Add-Result 'Auditing API startup' $apiReady $(if ($apiReady) { 'HTTP 200' } else { 'did not become ready' })
    Add-Result 'Identity API startup' $identityReady $(if ($identityReady) { 'HTTP 200' } else { 'did not become ready' })

    if (-not ($wfReady -and $apiReady -and $identityReady)) {
        throw 'Services did not become ready for smoke testing.'
    }

    $reference = Invoke-JsonRequest -Method 'POST' -Uri "$ApiBaseUrl/api/v1/RiskAssessment/CreateReference" -Headers $headers -Body @{
        Client = 'Smoke Review Client'
        AssessmentStartDate = '2026-03-01T00:00:00Z'
        AssessmentEndDate = '2026-03-31T00:00:00Z'
        Assessor = 'System Administrator'
        ApprovedBy = 'System Administrator'
    }
    $tempRef = [int]$reference.referenceId
    Add-Result 'Create throwaway reference' ($tempRef -gt 0) ("referenceId=$tempRef")

    $planningWorkflow = Invoke-JsonRequest -Method 'POST' -Uri "$ApiBaseUrl/api/v1/AuditWorkflow/StartPlanningApproval" -Headers $headers -Body @{
        ReferenceId = $tempRef
        EngagementTitle = 'Smoke Review Assessment'
        RequestedByName = 'System Administrator'
        ApproverUserId = 1
        ApproverName = 'System Administrator'
        Notes = 'Smoke review/sign-off path'
        DueDate = '2026-03-15T00:00:00Z'
    }

    Start-Sleep -Seconds 2
    $reviewsByReference = Invoke-JsonRequest -Method 'GET' -Uri "$ApiBaseUrl/api/v1/AuditReviews/GetByReference/$tempRef" -Headers $headers
    $reviewCount = @($reviewsByReference).Count
    Add-Result 'Generic review creation' ($reviewCount -ge 1) ("workflowInstanceId=$($planningWorkflow.workflowInstanceId); reviews=$reviewCount")

    $workspaceResponse = Invoke-JsonRequest -Method 'GET' -Uri "$ApiBaseUrl/api/v1/AuditReviews/GetWorkspace?userId=1" -Headers $headers
    $workspaceReviews = Get-ObjectList -Object $workspaceResponse -Names @('reviews', 'Reviews')
    $workspaceOk = @($workspaceReviews | Where-Object { $_.referenceId -eq $tempRef -or $_.ReferenceId -eq $tempRef }).Count -ge 1
    Add-Result 'Review workspace load' $workspaceOk ("workspaceReviews=$(@($workspaceReviews).Count)")

    try {
        $taskId = 0
        $workflowInstanceId = $planningWorkflow.workflowInstanceId
        if ([string]::IsNullOrWhiteSpace($workflowInstanceId)) {
            $workflowInstanceId = $planningWorkflow.WorkflowInstanceId
        }

        $inbox = Invoke-JsonRequest -Method 'GET' -Uri "$ApiBaseUrl/api/v1/AuditWorkflow/GetInbox?userId=1" -Headers $headers
        $pendingTasks = Get-ObjectList -Object $inbox -Names @('pendingTasks', 'PendingTasks', 'tasks', 'Tasks')
        $task = $pendingTasks | Where-Object {
            ($_.workflowInstanceId -eq $workflowInstanceId) -or
            ($_.WorkflowInstanceId -eq $workflowInstanceId) -or
            ($_.referenceId -eq $tempRef) -or
            ($_.ReferenceId -eq $tempRef)
        } | Select-Object -First 1

        if ($null -ne $task) {
            $taskId = if ($null -ne $task.id) { [int]$task.id } else { [int]$task.Id }
        }

        if ($taskId -gt 0) {
            $completionDetail = 'completed'
            try {
                $null = Invoke-JsonRequest -Method 'PUT' -Uri "$ApiBaseUrl/api/v1/AuditWorkflow/CompleteTask/$taskId" -Headers $headers -Body @{
                    CompletionNotes = 'Smoke review approved'
                }
            }
            catch {
                $completionDetail = $_.Exception.Message
            }

            Start-Sleep -Seconds 2

            $signoffCount = 0
            $signoffDetail = ''
            try {
                $signoffs = Invoke-JsonRequest -Method 'GET' -Uri "$ApiBaseUrl/api/v1/AuditReviews/GetSignoffsByReference/$tempRef?limit=20" -Headers $headers
                $signoffCount = @($signoffs).Count
                $signoffDetail = "apiSignoffs=$signoffCount"
            }
            catch {
                $signoffCount = [int](Invoke-SqlScalar -ConnectionString $connectionString -Sql "SELECT COUNT(*) FROM ""Risk_Assess_Framework"".audit_signoffs WHERE reference_id = $tempRef;")
                $signoffDetail = "apiReadFailed=$($_.Exception.Message); dbSignoffs=$signoffCount"
            }

            Add-Result 'Generic sign-off completion' ($signoffCount -ge 1) ("taskId=$taskId; completion=$completionDetail; $signoffDetail")
        } else {
            Add-Result 'Generic sign-off completion' $false 'No pending workflow inbox task found for smoke reference'
        }
    }
    catch {
        Add-Result 'Generic sign-off completion' $false $_.Exception.Message
    }

    $upload = Invoke-FormCurl -Uri "$ApiBaseUrl/api/v1/AuditDocuments/UploadDocument" -HeaderLines $curlHeaders -FormLines @(
        "ReferenceId=$tempRef",
        'Title=Smoke Review Document',
        'SourceType=Audit Team',
        'UploadedByName=System Administrator',
        'UploadedByUserId=1',
        "File=@$docPath;type=text/plain"
    )

    if ($upload.StatusCode -lt 200 -or $upload.StatusCode -ge 300) {
        throw "Document upload failed. HTTP $($upload.StatusCode): $($upload.Body)"
    }

    $uploadedDocument = $upload.Body | ConvertFrom-Json
    $documentId = [int]$uploadedDocument.id
    $accessBefore = [int](Invoke-SqlScalar -ConnectionString $connectionString -Sql "SELECT COUNT(*) FROM ""Risk_Assess_Framework"".audit_document_access_logs WHERE document_id = $documentId;")

    $null = Invoke-JsonRequest -Method 'GET' -Uri "$ApiBaseUrl/api/v1/AuditDocuments/GetDocument/$documentId" -Headers $headers
    $downloadHeaders = @{}
    foreach ($key in $headers.Keys) {
        $downloadHeaders[$key] = $headers[$key]
    }
    Invoke-WebRequest -Uri "$ApiBaseUrl/api/v1/AuditDocuments/DownloadDocument/$documentId" -Headers $downloadHeaders -OutFile $downloadPath -UseBasicParsing | Out-Null
    Start-Sleep -Milliseconds 500
    $accessAfter = [int](Invoke-SqlScalar -ConnectionString $connectionString -Sql "SELECT COUNT(*) FROM ""Risk_Assess_Framework"".audit_document_access_logs WHERE document_id = $documentId;")
    Add-Result 'Document access logging' ($accessAfter -ge ($accessBefore + 2)) ("documentId=$documentId; before=$accessBefore; after=$accessAfter")

    $userRow = Invoke-SqlRow -ConnectionString $connectionString -Sql @'
SELECT
    a.user_id,
    a.username,
    a.email,
    a.password,
    TRIM(COALESCE(a.firstname, '') || ' ' || COALESCE(a.lastname, '')) AS display_name
FROM "Risk_Assess_Framework".accounts a
WHERE COALESCE(a.is_active, TRUE) = TRUE
  AND a.email IS NOT NULL
  AND a.password IS NOT NULL
ORDER BY a.user_id
LIMIT 1;
'@

    if ($null -eq $userRow) {
        throw 'Could not find an active account row for identity login smoke test.'
    }

    $loginBefore = [int](Invoke-SqlScalar -ConnectionString $connectionString -Sql "SELECT COUNT(*) FROM ""Risk_Assess_Framework"".audit_login_events WHERE user_id = $([int]$userRow.user_id);")
    $encodedEmail = [System.Uri]::EscapeDataString([string]$userRow.email)
    $encodedPassword = [System.Uri]::EscapeDataString([string]$userRow.password)
    $loginResponse = Invoke-WebRequest -Uri "$IdentityBaseUrl/api/v1/UserLogin/login?email=$encodedEmail&password=$encodedPassword" -UseBasicParsing -ErrorAction Stop
    Start-Sleep -Milliseconds 500
    $loginAfter = [int](Invoke-SqlScalar -ConnectionString $connectionString -Sql "SELECT COUNT(*) FROM ""Risk_Assess_Framework"".audit_login_events WHERE user_id = $([int]$userRow.user_id);")
    Add-Result 'Login event logging' (($loginResponse.StatusCode -eq 200) -and ($loginAfter -ge ($loginBefore + 1))) ("userId=$($userRow.user_id); before=$loginBefore; after=$loginAfter")

    if ($tempRef) {
        $archive = Invoke-JsonRequest -Method 'POST' -Uri "$ApiBaseUrl/api/v1/AuditPlatform/ArchiveAssessment/$tempRef" -Headers $headers -Body @{
            ArchivedByUserId = 1
            ArchivedByName = 'System Administrator'
            Reason = 'Smoke cleanup'
        }
        Add-Result 'Archive smoke reference' ([bool]($archive.success)) ("referenceId=$tempRef")
    }
}
finally {
    foreach ($proc in @($identityProc, $apiProc, $wfProc)) {
        if ($null -ne $proc -and -not $proc.HasExited) {
            try {
                Stop-Process -Id $proc.Id -Force
            }
            catch {
            }
        }
    }

    $results | Format-Table -AutoSize | Out-String | Set-Content -Path $resultsPath
    $results | Format-Table -AutoSize
}

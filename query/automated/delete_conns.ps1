# Function to get connections containing 'kubernetes' in the foreign address
function Get-KubernetesConnections {
    return (Invoke-Expression "netstat" | Select-String -Pattern 'kubernetes')
}

# Function to parse the netstat output into a custom object with properties
function Parse-NetstatOutput {
    param($output)

    if ($output -match '(\S+)\s+(\S+)\s+(\S+)\s+(\S*)\s*(\d+)') {
        return @{
            Protocol = $matches[1]
            LocalAddress = $matches[2]
            ForeignAddress = $matches[3]
            State = $matches[4]
            ProcessId = $matches[5]
        }
    }
}

# Get the list of connections containing 'kubernetes'
$kubernetesConnections = Get-KubernetesConnections

# Iterate through each connection and close it
foreach ($connection in $kubernetesConnections) {
    # Extract the process ID (ProcessId) from the connection object
    $processId = (Parse-NetstatOutput $connection).ProcessId

    # Close the connection by terminating the process associated with the ProcessId
    if ($processId -ne $null) {
        try {
            Stop-Process -Id $processId -Force -ErrorAction Stop
            Write-Host "Closed connection with ProcessId: $processId"
        } catch {
            Write-Host "Failed to close connection with ProcessId: $processId"
        }
    } else {
        Write-Host "Failed to parse netstat output: $connection"
    }
}



while ($true) {
    #Start Docker
    Start-Process "C:\Program Files\Docker\Docker\frontend\Docker Desktop.exe"
    #Wait for 3 minutes for docker to start up
    Start-Sleep -Seconds (3 * 60)
    #Start prometheus
    Invoke-Expression "docker start prometheus"
    #Give it a few seconds for prometheus to start
    Start-Sleep -Seconds 5
    try {
        python program.py

        # Wait for 20 minutes (20*60 seconds)
        $isrunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
        if ($isrunning) {
            $isrunning.CloseMainWindow()
            $isrunning | Stop-Process -Force
        }
        else{

            $dockerprocesses = Get-Process "*docker desktop*"
            foreach($process in $dockerprocesses)
            {
                try{
                    $process.Kill()
                }
                catch{
                    Write-Host "Failed to kill a docker process"
                }
            }
        }
        
    }
    catch {
        # Log the error message (optional)
        Write-Host "An error occurred: $_"

        break
    }
}

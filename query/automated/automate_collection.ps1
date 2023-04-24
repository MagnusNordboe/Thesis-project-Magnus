while ($true) {
    try {
        # Replace "your_python_script.py" with the name of your Python script
        # Add any parameters after the script name if needed
        python your_python_script.py

        # Wait for 20 minutes (20*60 seconds)
        Start-Sleep -Seconds (20 * 60)
    }
    catch {
        # Log the error message (optional)
        Write-Host "An error occurred: $_"

        # Wait for 20 minutes (20*60 seconds) before retrying
        Start-Sleep -Seconds (20 * 60)
    }
}

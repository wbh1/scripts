function OfflineWUCheck {

    param ([Parameter(Mandatory=$true,Position=0)] $file)
    
    #using WU API, as documented at https://goo.gl/E1FKVR

    #get an updateservicemanager interface, https://goo.gl/bltX5q
    #then register our downloaded wsusscn2.cab as an update service, https://goo.gl/g00yVA
    $UpdateServiceManager = New-Object -ComObject 'Microsoft.Update.ServiceManager'
    $UpdateService = $UpdateServiceManager.AddScanPackageService("wsusscn2 file", $file)

    #Setup a searcher, have it use the newly registered updateservice
    $Searcher = New-Object -ComObject Microsoft.Update.Searcher
    $Searcher.ServerSelection = 3
    $Searcher.ServiceID = $UpdateService.ServiceID

    Write-Host "Will search $($UpdateService.Name), $($UpdateService.ServiceID)"
    Write-Host "Beginning search using $($Searcher.ServiceID) $($Searcher.Name)"

    #$SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software' and IsHidden=0")
    $SearchResult = $Searcher.Search("IsInstalled=0 and IsHidden=0")
    $Updates = $SearchResult.Updates

    Write-Host "$($Updates.Count) outstanding updates"
    if ($Updates.Count -ne 0){
        foreach ($Update in $Updates) {
            $dlsize = $($Update.MaxDownloadSize)/1MB
            $dlsize = "{0:N1}" -f $dlsize
            Write-host "$($Update.KBArticleIDs), $($Update.MSRCSeverity),  $dlsize MB"
        }
    }
}

$file = "C:\Users\wbhegedusk2030\Downloads\Wsusscn2.cab"

$sig = Get-AuthenticodeSignature -FilePath $file

if ($sig.Status -eq "Valid") { 
    Write-Host "Beginning offline WU check "
    $checktime = Measure-command {OfflineWUCheck -file $file}
    Write-Host "Offline WU check completed in $($checktime.Minutes) minutes."
}
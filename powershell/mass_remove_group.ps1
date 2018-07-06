param (
    [Parameter(Mandatory=$true)][string]$ADGroup,
    [switch]$RemoveAll = $false,
    [switch]$DeleteGroup = $false
)

Import-Module ActiveDirectory

function PrintADGroupMembers ($ADGroup) {
    Try {
        # Select-Object name
        $members = Get-ADGroupMember $ADGroup 
    } 
    Catch {
        Write-Host "Invalid group name -- please try again"
        exit
    }

    [string[]]$MemberList = @()

    foreach($user in $members) {
        Write-Host $user.name
        $MemberList += $user.name
    }
    return

}

function RemoveADGroupMembers ($ADGroup) {
    $members = Get-ADGroupMember $ADGroup

    foreach($user in $members){
        Try {
            Remove-ADGroupMember -Identity $ADGroup -Members $user.name -Confirm:$false
            Write-Host Successfully removed $user.name from $ADGroup
        } 
        Catch {
            Write-Host "ERROR: Could not remove $user.name from $ADGroup"
        }
    }

    if ($DeleteGroup) {
        $confirmation = Read-Host "You want to remove // $ADGroup // FOREVER? [y/n]"
    
        while($confirmation -ne "y") {
            if ($confirmation -eq 'n') {
                Write-Host "OK then we're done here."
                return
            }
            $confirmation = Read-Host "You want to remove // $ADGroup // FOREVER? [y/n]"
        }

        Try {
            Remove-ADGroup $ADGroup -Confirm:$false
            Write-Host "Successfully deleted $ADGroup"
        }
        Catch {
            Write-Host "Failed to delete $ADGroup"
        }
    }
}

if ($RemoveAll) {
    
    PrintADGroupMembers($ADGroup)

    $confirmation = Read-Host "You want to remove all users from // $ADGroup //? [y/n]"
    
    while($confirmation -ne "y") {
        if ($confirmation -eq 'n') {
            exit
        }
        $confirmation = Read-Host "You want to remove all users from $ADGroup ? [y/n]"
    }

    RemoveADGroupMembers($ADGroup)
    exit
}

<#
Upload articles and images to my wiki. 

https://www.mediawiki.org/wiki/API:Edit
#>
[CmdletBinding(SupportsShouldProcess)]
param(
  [Parameter(Mandatory,ValueFromPipeline)]
  [string[]]$infiles,
  [string]$CredentialFile = (Join-Path $PSScriptRoot "un_pw.json"),
  [scriptblock]$WikiName = { $_.BaseName -replace '_',' ' },
  [scriptblock]$WikiComment = { "Upload of $($_.Name)" }
)
BEGIN {
  # Make sure the un_pw.json file is present... 
  if(Test-Path $CredentialFile) {
    $wiki = ConvertFrom-Json (Get-Content -Raw -Encoding utf8NoBOM -Path $CredentialFile)
    Write-Verbose "API endpoint is <$($wiki.url)>"
    Write-Verbose "Username is <$($wiki.uname)>"
  } else {
    Write-Error "Must have a JSON file named <$CredentialFile> with keys for (url, uname, pw) of the wiki."
    Exit 1
  }

  if ($PSCmdlet.ShouldProcess($wiki.url,"Get CSRF Token")) {
    # Step 1: GET request to fetch login token
    $params_0 = @{
      "action" = "query"
      "meta" = "tokens"
      "type" = "login"
      "format" = "json"
    }
    $data = Invoke-RestMethod -Uri $wiki.url -Method Get -SessionVariable WikiSession -Body $params_0
    $login_token = $data.query.tokens.logintoken
  
    # Step 2: POST request to log in. Use of main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    $params_1 = @{
      "action" = "login"
      "lgname" = $wiki.uname
      "lgpassword" = $wiki.pw
      "lgtoken" = $login_token
      "format" = "json"
    }
    Invoke-RestMethod -Uri $wiki.url -Method Post -WebSession $WikiSession -Body $params_1
  
    # Step 3: GET request to fetch CSRF token
    $params_2 = @{
      "action" = "query"
      "meta" = "tokens"
      "format" = "json"
    }
    $data = Invoke-RestMethod -Uri $wiki.url -Method Get -WebSession $WikiSession -Body $params_2
    $csrf_token = $data.query.tokens.csrftoken
  }
}
PROCESS {
  foreach ($fl in $infiles) {
    $my_wname = &$WikiName $fl
    Write-Verbose "Name on the Wiki will be <$my_wname>"

    $my_comment = &$WikiComment $fl
    Write-Verbose "The upload comment will be <$my_comment>"

    if ($PSCmdlet.ShouldProcess($fl, "Upload File")) {
      # Step 4: POST request to edit a page
      $params_3 = @{
        "action" = "edit"
        "title" = $my_wname
        "token" = $csrf_token
        "format" = "json"
        "text" = (Get-Content -Raw -Encoding utf8NoBOM -Path $fl)
      }
    
      Invoke-RestMethod -Uri $wiki.url -Method Post -WebSession $WikiSession -Body $params_3
    }
  }
}
# vim: sw=2:expandtab

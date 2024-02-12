# Wiki-Upload utility.

    usage: wiki-upload [-h] [-c CREDENTIALS] [-s SUMMARY] [-f TITLE] [--html] [filename ...]
    
    Upload files to a mediawiki
    
    positional arguments:
      filename
    
    options:
      -h, --help            show this help message and exit
      -c CREDENTIALS, --credentials CREDENTIALS
                            A JSON file of credentials (default: un_pw.json)
      -s SUMMARY, --summary SUMMARY
                            A summary comment to use for the files. {} == filename
      -f TITLE, --fetch TITLE
                            Fetch an article
      --html                Fetch as html instead of wikitext

The Credentials file should look like this:


    {
      "url": "https://whatever.wiki.com/api.php",
      "uname": "user name herer",
      "pw": "password here"
    }

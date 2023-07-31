# Build onefile executable using Nuitka:
My architecture (64-bit windows):
```
python -m nuitka --enable-plugin=tk-inter --disable-console --onefile RacingInsightsApp.py --include-package=boto3 --include-package=dynamodb-json --include-module=decimal --windows-icon-from-ico=images/RacingInsights_logo.ico --onefile-tempdir-spec="%CACHE_DIR%/%COMPANY%/%PRODUCT%/%VERSION" --company-name=Qnooperd --product-name=RacingInsights --file-version=0.0.2.1 --product-version=0.0.2.1
```

NOTE: Iracing only supports 64 bit windows 10 and 11. Hence no need for 32 bit support.

# GitHub Actions build:
```
name: Executable Build - Nuitka

on:
  workflow_dispatch:

env:
  APP_CLIENT_ID: ${{ secrets.APP_CLIENT_ID }}
  REGION: ${{ secrets.REGION }}

jobs:
  build:
    runs-on: windows-latest

    steps:
      # Check-out repository
      - uses: actions/checkout@v3
      
      # Setup Python
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          architecture: 'x64' # optional x64 or x86. Defaults to x64 if not specified
          cache: 'pip'
      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # Build python script into a stand-alone exe
      - uses: Nuitka/Nuitka-Action@main
        with:
          script-name: app.py
          module: false
          standalone: true
          onefile: false
          assume-yes-for-downloads: true
          enable-plugins: tk-inter
          # include-package: src
          # include-package-data:
          # include-module:
          # include-plugin-directory:
          # include-plugin-files:
          # prefer-source-code:

          output-dir: build
          # output-file: # Cannot be changed in standalone mode

          # access-token:

          enable-console: true
          # disable-console:

          windows-icon-from-ico: images/RacingInsights_logo.ico
          windows-uac-admin: false
          windows-uac-uiaccess: false
          windows-company-name: RacingInsights
          windows-product-name: RacingInsights-Overlays
          windows-file-version: 0.0.2.0
          windows-product-version: 0.0.2.0
          # windows-file-description:
          # windows-onefile-tempdir-spec:

          # macos-create-app-bundle:

      # Uploads artifact
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ runner.os }} Build
          path: build/
          if-no-files-found: error
```

# Make setup for executable and data files:
Using the inno setup tool and the script found ./setup/setup_script.iss.

Make sure to have any additional data files to be configured correctly as shown below. 
This is not done by the tool and needs to be done manually after the initial script creation.
<div align="center">
  <a href="">
    <img src="docs/guides/screenshots/setup_configuration_change.png" width="500" height=auto>
  </a>
</div>
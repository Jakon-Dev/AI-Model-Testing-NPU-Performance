# Installation for Qualcomm (ARM64) testing

## 1. Update all drivers
1. Search for updates from **Settings > Windows Update > Search for updates**.
2. Restart the computer to apply all driver updates.

## 2.  **Install Python**  
1. [Python Releases for Windows | Python.org](https://www.python.org/downloads/windows/)
2. Download the Windows installer (ARM64) for version 3.11.9.
3. Install Python 3.11.9, making sure to check the option to **add it to the PATH**:  
    <img width="857" height="430" alt="image" src="https://github.com/user-attachments/assets/dfc13c55-4d86-4ee7-a2f8-b15cbd86268e" />


## 3. Create a Python virtual environment
1. Open **PowerShell as administrator** and navigate to the folder where you want to create the virtual environment (in this example, everything will be in "C:/").
    ```powershell
    cd 'C:\'
    ```
2. Set the execution policy to allow scripts:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
    ```
3. Create the environment:
    ```powershell
    python -m venv ai-test
    ```
4. Activate the environment:
    ```powershell
    ai-test\Scripts\activate
    ```
5. Upgrade pip:
    ```powershell
    python -m pip install --upgrade pip
    ```

## 4. Create the folder for all installations
    cd 'C:\'
    mkdir ModelsONNX
    

## 5.  Install [Qualcomm - QNN | onnxruntime](https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html)
1. **Install the [Qualcomm AI Engine Direct SDK](https://docs.qualcomm.com/bundle/publicresource/topics/80-63442-50/windows_setup.html?product=1601111740009302)**  
   - Download the QNN SDK from [here](https://www.qualcomm.com/developer/software/qualcomm-ai-engine-direct-sdk)  
     - Press "Get Software".
     - Unzip the folder.  
     - Move the *`qairt/<SDK_VERSION>`* folder to a location where you want to call it *`qairt`* (this folder should contain subfolders like *bin, lib*...).  
   - **Configure the environment and dependencies**  
     - Access the downloaded "qairt" folder and then "bin".  
       - Go to the qairt folder with "cd" and then into "bin":
                ```powershell
                cd qairt
                cd bin
                ```
      - Set the environment variables:
                ```powershell
                .\envsetup.ps1
                ```
                **ATTENTION:** The *`envsetup.ps1`* script will only update the environment variables for **THIS** PowerShell session. If you need to set them again (e.g., in a new terminal), you must re-run the script.

            3. Verify and install Windows dependencies:
                ```powershell
                & "${QAIRT_SDK_ROOT}/bin/check-windows-dependency.ps1"
                ```
                Run this command until the script says "All Done", as it will be installing various dependencies like Visual Studio and Visual Studio Build Tools.
                <img width="1567" height="744" alt="image" src="https://github.com-attachments/assets/4e05114c-d171-403d-a5d8-22f658a212c5" />

            4. Verify the installation:
                ```powershell
                & "${QAIRT_SDK_ROOT}/bin/envcheck.ps1" -m
                ```
                You should see an output similar to the following:
                ```powershell
                Checking MSVC Toolchain
                --------------------------------------------------------------
                WARNING: The version of VS BuildTools 14.40.33807 found has not been validated. Recommended to use known stable VS BuildTools version 14.34
                WARNING: The version of Visual C++(x64) 19.40.33812 found has not been validated. Recommended to use known stable Visual C++(x64) version 19.34
                WARNING: The version of CMake 3.28.3 found has not been validated. Recommended to use known stable CMake version 3.21
                WARNING: The version of clang-cl 17.0.3 found has not been validated. Recommended to use known stable clang-cl version 15.0.1
                  Name                                     Version
                  --------                                 ----------
                Visual Studio                          17.10.35027.167
                VS Build Tools                         14.40.33807
                Visual C++(x86)                        19.40.33812
                Visual C++(arm64)                      Not Installed
                Windows SDK                            10.0.22621
                CMake                                  3.28.3
                clang-cl                               17.0.3
                --------------------------------------------------------------
                ```
                The only required dependencies are **CMake, clang-cl, Visual Studio, and VS Build Tools**. It's okay if the C++ dependencies show as "Not Installed".

    b. **Install CMake 3.28 or higher**
        i. This installation should only be done if the previously installed version (shown in the verification from the previous step) is not 3.28 or higher.
        ii. [Download CMake](https://cmake.org/download/)

    c. **Install onnxruntime requirements**
        ```powershell
        cd 'C:\ModelsONNX'
        
        git clone --recursive [https://github.com/Microsoft/onnxruntime.git
        
        cd onnxruntime
        
        pip install -r requirements.txt
        

## 6.  **Download ONNX test models**
    a. Go to the folder where the models will be downloaded:
        ```powershell
        cd 'C:\ModelsONNX'
        ```
    b. Download the models:
        i. **OPTIONAL:** By default, downloads using *`Invoke-WebRequest`* will show a progress bar that makes the download about 10 times longer. This is good for checking that it's downloading, but for faster speed, you can remove it by running:
            ```powershell
            $ProgressPreference = 'SilentlyContinue'
            ```
            And to show the progress bar again:
            ```powershell
            $ProgressPreference = 'Continue'
            ```

| Model | Approx. Size | PowerShell Command |
| :--- | :--- | :--- |
| **MobileNetV2** | ~14 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/mobilenet/model/mobilenetv2-7.onnx?raw=true" -OutFile "mobilenetv2.onnx"` |
| **SqueezeNet** | ~5 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/squeezenet/model/squeezenet1.1-7.onnx?raw=true" -OutFile "squeezenet.onnx"` |
| **ResNet50** | ~100 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/resnet/model/resnet50-v1-7.onnx?raw=true" -OutFile "resnet50.onnx"` |
| **Inception v2** | ~44 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/inception_and_googlenet/inception_v2/model/inception-v2-9.onnx?raw=true" -OutFile "inceptionv2.onnx"` |
| **ResNet101** | ~175 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/resnet/model/resnet101-v1-7.onnx?raw=true" -OutFile "resnet101.onnx"` |
| **DenseNet121-7** | ~32 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/densenet-121/model/densenet-7.onnx?raw=true" -OutFile "densenet121_7.onnx"` |
| **DenseNet121-12** | ~8 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/densenet-121/model/densenet-12-int8.onnx?raw=true" -OutFile "densenet121_12.onnx"` |
| **EfficientNet-lite4-11** | ~51 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11.onnx?raw=true" -OutFile "efficientnet_lite4_11.onnx"` |
| **BERT Large (SQuAD)** | ~418 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/text/machine_comprehension/bert-squad/model/bertsquad-10.onnx?raw=true" -OutFile "bert-large-squad.onnx"` |
| **RoBERTa Base** | ~500 MB | `Invoke-WebRequest -Uri "https://github.com/onnx/models/blob/main/validated/text/machine_comprehension/roberta/model/roberta-base-11.onnx?raw=true" -OutFile "roberta-base.onnx"` |

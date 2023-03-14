# VIDEO QUALITY METRICS TOOLKIT - VQMTK

## Cite
This repository contains the artifacts submitted to publication to SoftwareX (this is a provisional bibtex entry):

```bib
@article{doi,
authors={Wilmer Moina-Rivera and Juan Gutiérrez-Aguado and Miguel Garcia-Pineda},
journal={SoftwareX},
title={Video Quality Metrics Toolkit: An Open Source Software to Assess Video Quality},
vol={Under revision},
year={2023},
doi={},
}
```
If you use this container, please cite that paper.
## Run the container and explore the Jupyter notebooks

In the following we assume that you are using the dockerhub image, if you want to use the local built image change the image to `vqmt:latest`.

### Run the container using the sample videos included in the image

Start the container
```sh
docker run --name vqmtk -d -p 8888:8888 -p 8050:8050 -e JUPYTER_ENABLE_LAB=yes  cloudmedialab/vqmtk:latest
```

Once the container is executed we must check the logs (this works in Linux, in other OS you must just run `docker logs vqmtk` and search for the URL):

```sh
docker logs vqmtk | grep "http://127" | tail -n1 | awk -F"or" '{print $2}'
```
to obtain the URL that can be used to open the Jupyter notebooks included in the image. Open that URL in a browser.

The image contains some videos, some notebooks that illustrate how to obtain the metrics, and the results already computed. If you want to see the plots you do not need to run the scripts.

![Sample notebook included in the image)](./screenshots/sample_notebook.png)

To stop the container:
```sh
docker stop vqmtk
```

To start again the container:
```sh
docker start vqmtk
```
If you do not remember the URL to access Jupyter then you can search again in the logs of the container.

You can check if the container is running with the following command:
```sh
docker ps
```

To delete the container (**be carefull**: all the information not stored in a mounted volume will be lost):
```sh
docker rm vqmtk
```
You cannot run two containers with the same name in the same machine. You can assign a different name to the second one or delete the first one.

### Run the container providing your videos
In the following, we assume that there is a folder in your file system name `MY_FOLDER`with a subfolder `experiments` that contains subfolders `videos` and `results`.
The `videos` subfolder contains the videos that you want to analyze. The `results` folder will contain the results of the metrics.

You can store the notebooks in the `experiments` subfolder (this replicates the structure provided in the `examples` folder).

Assuming that you are in the folder `MY_FOLDER`, you can start the container with the following command:

```sh
docker run --name vqmtk -d -p 8888:8888 -p 8050:8050 -e JUPYTER_ENABLE_LAB=yes -v "${PWD}":/home/jovyan/work/experiments cloudmedialab/vqmtk:latest
```
Inside Jupyter we can see a new folder named `experiments` (inside the folder `work`)  and all the files created inside this folder will be stored in our file system.

### Remote access as a service
For remote access, we recommend to use this container along with Nginx and a valid certificate, and use `docker-compose` to start both containers. This is out of the scope of this project, you can find documentation elsewhere.


## Run the vqmcli script included in the container

List the allowed options of the script:
```sh
docker run --rm --name vqmcli cloudmedialab/vqmtk:latest vqmcli -h
```

We are deleting the container after the execution of the script (with the `--rm` option).

For example, assuming that you have a `videos` directory in your file system (with the reference and distorted videos), the following command will compute the metrics:

```sh
VIDEOS_PATH=<WRITE HERE THE FULL PATH OF THE VIDEOS DIRECTORY>
docker run --rm --name vqmcli -u $(id -u):$(id -u) -v ${VIDEOS_PATH}:/videos cloudmedialab/vqmtk:latest vqmcli -r /videos/video-ref.mp4 -d /videos/video-dis.mp4 -o /videos/vmaf -v
```

If the name of the directory where the experiment results will be stored is not specified, the default **VQMCore_Results** directory is created in the root of the mounted directory.


## Supported video codecs per container for each quality metric
| Container 	|  MP4  	|       	|     	|     	|  MKV  	|       	|     	|     	| WEBM 	|     	| RAW 	|
|:---------:	|:-----:	|:-----:	|:---:	|:---:	|:-----:	|:-----:	|:---:	|:---:	|:----:	|:---:	|:---:	|
|   Codec   	| H.264 	| H.265 	| VP9 	| AV1 	| H.264 	| H.265 	| VP9 	| AV1 	|  VP9 	| AV1 	| Y4M 	|
|   APSNR   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|  BRISQUE  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|   CAMBI   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
| CIEDE2000 	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|   MSSSIM  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    NIQE   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    PSNR   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|  PSNRHVS  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    SSIM   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|   STRRED  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    VIF    	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|   VIIDEO  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    VMAF   	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|
|    VQM    	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓   	|   ✓   	|  ✓  	|  ✓  	|   ✓  	|  ✓  	|  ✓  	|


## Build docker image locally
Alternatively, you can build the image locally using the provided Dockerfile.

Clone this repository:
```sh
git clone https://github.com/cloudmedialab-uv/vqmtk.git
```

Change to cloned directory:
```sh
cd vqmtk
# Change to docker subdirectory
cd docker
```
Make changes to the `Dockerfile` to adapt the container to your needs.

Create container image (this can take more than 45 minutes depending on the hardware where the image is created) and store output in log file.
The name of the image created is `vqmtk:latest`.
```sh
nohup docker build -t vqmtk:latest . > create_container.log
```

Once the image is built, you can start the container using the local created image:

```sh
docker run --name vqmtk -d -p 8888:8888 -p 8050:8050 -e JUPYTER_ENABLE_LAB=yes vqmtk:latest
```
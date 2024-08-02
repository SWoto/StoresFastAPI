# StoresFastAPI
An API for simulated stores built using FastAPI and AWS

# How to
It uses docker to run containers, to run the api, just use the command:
```
docker compose up
```
or 
```
docker compose up --build
```
to force building the containers.

To test, open the container where the api is running, outsite `src` (`/home`) folder and run `pytest --log-cli-level=DEBUG --durations=-0`
 
It is also possible to test functions individually:
```python
pytest src/tests/api/v1/endpoints/test_users.py::TestUser::test_confirm_user --log-cli-level=DEBUG --durations=-0

pytest src/tests/api/v1/endpoints/test_users.py::TestUser --log-cli-level=DEBUG --durations=0
pytest src/tests/api/v1/endpoints/test_stores.py::TestStore --log-cli-level=DEBUG --durations=0
pytest src/tests/api/v1/endpoints/test_products.py::TestProduct --log-cli-level=DEBUG --durations=0
```

# AWS

## EC2 Instance and SSH using VSCode

This guide provides instructions on setting up an SSH connection to an AWS EC2 instance using Visual Studio Code (VSCode). If you have a new AWS account, you can utilize the free tier options. Otherwise, there are several affordable services available.

### Prerequisites
- An AWS account
- Visual Studio Code installed
- A basic understanding of AWS EC2 and SSH

### Step 1: Launch an EC2 Instance

For this project, we will use the `Amazon Linux 2023 AMI` Image with the `t2.micro` instance type. You can choose other configurations based on your requirements.

1. **Log in to the AWS Management Console.**
2. **Navigate to the EC2 Dashboard.**
3. **Launch a new instance**:
   - Select the `Amazon Linux 2023 AMI`.
   - Choose the `t2.micro` instance type.
   - Configure instance details, add storage, and add tags as needed.
   - Configure the security group to allow SSH access (port 22) and "All ICMP - IPv4" from your IP address.
4. **(Optional) Spot instances**:
   - For test projects where an always-on instance is not required, it is advisable to use Spot Instances to reduce costs. Spot Instances are generally cheaper than On-Demand Instances and can be a cost-effective choice if instance availability and interruptions are not a concern.
5. **(Optional) Create a Budget Alert**:
   - To avoid unexpected bills, it is recommended to create a budget alert for costs exceeding the free tier (e.g., USD 0.01). "Who never received an unepected bill from aws?".
   - Follow the template for the Zero spend budget configuration on the [Billing Console](https://console.aws.amazon.com/billing/home#/budgets).


### Step 2: Retrieve Instance Information

You will need the following information from your EC2 instance:

- **Public DNS**: The public address of your instance.
- **Default User**: Typically `ec2-user` for Amazon Linux.

Refer to the AWS documentation for more details: [Get information about your instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-to-linux-instance.html#connection-prereqs-get-info-about-instance).

### Step 3: (Optional) Basic Connectivity Test

To perform a basic connectivity test:

- **Ping the Public DNS**:
   ```bash
   ping ec2-a-b-c-d.us-west-2.compute.amazonaws.com
   ```

### Step 4: Connect to Your Instance via SSH (Without VSCode)

1. **Set Permissions for the Private Key File**:
   Change the permissions of your private key file to ensure it is not publicly viewable. (Mandatory or the connection will fail)
   ```bash
   chmod 400 /path/to/key-pair-name.pem
   ```
2. **Connect to the Instance:**
    Use the SSH command to connect to your instance.
    ```bash
    ssh -i /path/to/key-pair-name.pem ec2-user@ec2-a-b-c-d.us-west-2.compute.amazonaws.com
    ```

### Step 5: Integrate with Visual Studio Code

1. **Open VSCode** and press `F1` to open the command palette.
2. **Type and select** `Remote-SSH: Connect to Host...`.
3. **Select: Configure SSH Hosts** and choose the config file.
4. **Configure the config file**:
   ```
   # Read more about SSH config files: https://linux.die.net/man/5/ssh_config
   Host AWS-EC2-StoresFastAPI
       HostName ec2-a-b-c-d.us-west-2.compute.amazonaws.com
       User ec2-user
       IdentityFile /path/to/key-pair-name.pem
   ```
5. **Type and select** `Remote-SSH: Connect to Host...`.
6. **Select the created host on step 4.**

## RDS Instance (AWS)

To set up a managed PostgreSQL database that integrates with the previously created EC2, follow these steps:

1. **Log in to the AWS Management Console.**
2. **Navigate to the RDS Dashboard**:
   - In the AWS Management Console, find and click on `RDS` under the `Database` category.
3. **Choose a Database Creation Method**:
   - Select `Easy create` to simplify the setup process.
4. **Select Database Engine**:
   - Choose `PostgreSQL`. Note that selecting `Aurora Compatible with PostgreSQL` will incur additional costs.
5. **Choose the DB Instance Size**:
   - Select the `Free tier` option to avoid charges. If other instance sizes are selected, it will result in charges.
6. **Credentials Manager**:
   - If planning to run the EC2 and RDS instances for more than a month, choose `Self managed` for the credentials manager. AWS Secrets Manager (AWS-SM) is only free for the first month.
7. **Set Up EC2 Connection**:
   - In `Set up EC2 connection`, select `Connect to an EC2 compute resource`.
   - Choose the previously created EC2 instance to allow connectivity between the EC2 and RDS instances.
8. **Create Database**:
   - Review the settings and click on `Create database` to launch the RDS instance.

**NOTE:** It is always good to emphasize the importance of creating a Budget Alert. Instructions are in Step 1 of the Setup SSH Connection section.

## Docker on EC2
The operating system does not have Docker installed by default, so it needs to be installed manually.

1. **Install Docker**:
   ```
   sudo yum update -y
   sudo yum -y install docker
   ```

2. **Start Docker**:
   ```
   sudo service docker start
   ```

3. **Allow the ec2-user to Access Docker Commands**:
   ```
   sudo usermod -a -G docker ec2-user
   ```

4. **Check Docker version**:
   - Reboot the instance.
   - Check the Docker version to ensure it is installed correctly:
   ```
   docker version
   ```

5. **Install Compose CLI plugin**
    - Follow the instructions at [Install the plugin manually](https://docs.docker.com/compose/install/linux/#install-the-plugin-manually)


## Setup the Repository

Git is not installed by default on Amazon Linux. Use the `yum` (Yellowdog Updater, Modified) command to install it.

1. **Update your system and install Git**:
   ```bash
   sudo yum update && sudo yum install git
   ```

2. **Clone this repository**:
   ```bash
   git clone https://github.com/SWoto/StoresFastAPI.git
   ```

3. **Folders and Permissions**
   - As instructed in [Mapped Files and Directories](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html#mapped-files-and-directories), database folder needs to have the propper permissions,
   ```
   sudo chown -R 5050:5050 <host_directory>
   ```

4. **Open the folder within the EC2 through VSCode**
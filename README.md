# JRD-PoC-AI

## Init project on Mac

Creates and activates a virtual environment into which it installs all the necessary dependencies to run the project.

```bash
source ./scripts/setup.sh
```

## Run FastAPI

```bash
./run.sh
```

## Aktivace venv

```bash
source .venv/bin/activate 
```

## Ngrok Setup

### On Mac

1. **Install ngrok:**

    ```bash
    brew install ngrok
    ```

2. **Test ngrok installation:**

    ```bash
    ngrok -h
    ```

3. **Create an Ngrok account:**

    Sign up at [Ngrok Signup](https://dashboard.ngrok.com/signup). Get your Authtoken.

4. **Add authtoken in terminal**
    
    ```bash
    ngrok config add-authtoken TOKEN
    ```

5. **Run ngrok for the desired port:**

    ```bash
    ngrok http 8880
    ```

6. **Access your app:**

    Access your app at address given at forwarding row:

    ```
    Forwarding  https://d0ea-193-179-66-16.ngrok-free.app -> http://localhost:8880    
    ```

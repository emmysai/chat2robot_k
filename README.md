# chat2robot_k_final

# Project: LLM-Based Robot Control for ROS2

This project implements a chatbot-based control interface for a TurtleBot3 robot in ROS2.
The robot can be commanded using natural language instead of directly entering coordinates.

The system combines an LLM, RAG, chat history, agentic tool calling and ROS2 communication.
The chatbot retrieves target poses from a local knowledge base, decides whether a robot command can be executed, and publishes the selected goal to ROS2.

# Getting Started

## Installation

Step-by-step instructions to set up and run the project.

## 1. Clone the Repository

```bash
git clone https://github.com/emmysai/chat2robot_k.git
cd chat2robot_k
```

## 2. Docker Setup

Change to the Docker folder:

```bash
cd docker
```

Build the Docker image:

```bash
docker compose build
```

Start the ROS2 service:

```bash
docker compose up -d ros2
```

Check whether the container is running:

```bash
docker ps
```

The container should appear with the name:

```text
ros2k
```

Access the running container:

```bash
docker exec -it ros2k bash
```

## 3. Build the ROS2 Workspace

Inside the container:

```bash
source /opt/ros/humble/setup.bash
cd /workspace/ros2_ws
colcon build
source install/setup.bash
```

If no source files were changed, rebuilding the workspace is not required every time.

## 4. Launch the ROS2 Simulation

Start the complete TurtleBot3 simulation:

```bash
ros2 launch turtlebot3_full_bringup full_bringup.launch.py
```

The launch file starts the components required for the simulation, including:

- Gazebo
- TurtleBot3
- Robot State Publisher
- Nav2
- AMCL
- Map Server
- RViz

## 5. Start the Chatbot

Open a new terminal and enter the running container:

```bash
docker exec -it ros2k bash
```

Source ROS2 and the workspace:

```bash
source /opt/ros/humble/setup.bash
source /workspace/ros2_ws/install/setup.bash
```

Change to the scripts folder:

```bash
cd /workspace/ros2_ws/src/turtlebot3_full_bringup/scripts
```

Start the Streamlit application:

```bash
streamlit run streamlit_app.py
```

The user interface is available in the browser at:

```text
http://localhost:8501
```

## 6. Google Gemini API Key

The chatbot uses Google Gemini.

The API key must not be committed to GitHub.

The project can request the API key at runtime if the environment variable is not set.

Alternatively, set the key before starting the chatbot:

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

Files such as `key.txt`, `kex.txt` and `.env` should be included in `.gitignore`.

# Example Commands

The chatbot can be controlled with natural language, for example:

```text
Fahr zu Pose A.
```

```text
Fahr zu Pose B.
```

```text
Fahr zur Home-Position.
```

For an ambiguous request such as:

```text
Fahr zu einer Position.
```

the agent should ask the user which target is intended.

The following answer can then be interpreted using the chat history:

```text
Pose B.
```

# System Architecture

```text
User
  |
  v
Streamlit UI
  |
  v
ask_agent()
  |
  +--------------------+
  |                    |
  v                    v
RAG / FAISS        Chat History
  |
  v
Gemini LLM
  |
  v
LangChain Tool-Calling Agent
  |
  v
ROS_send_goal(x, y, theta)
  |
  v
ROSGoalPublisher
  |
  v
/goal_pose
  |
  v
Nav2
  |
  v
/cmd_vel
  |
  v
TurtleBot3 in Gazebo
```

# RAG

The knowledge base is stored in:

```text
Angabe.tex
```

The RAG pipeline performs the following steps:

1. Load the text from `Angabe.tex`
2. Split the text into chunks
3. Generate embeddings using Gemini Embeddings
4. Store the vectors in a local FAISS vector store
5. Convert the user query into an embedding
6. Retrieve the most similar chunks
7. Pass the retrieved context together with the user request to the LLM

Current chunking parameters:

```text
chunk_size = 400
chunk_overlap = 50
```

The similarity search returns:

```text
k = 3
```

relevant chunks.

# LLM and Agent

The project uses LangChain together with Google Gemini.

The agent receives:

- a system prompt
- the user request
- retrieved RAG context
- chat history
- available tools

The agent decides whether enough information is available to execute the robot command.

If the target is clear and the coordinates are known, the agent can call:

```text
ROS_send_goal(x, y, theta)
```

If the target is unclear, the chatbot asks the user for additional information.

# ROS2 Communication

The ROS tool publishes a:

```text
geometry_msgs/msg/PoseStamped
```

message to:

```text
/goal_pose
```

The target coordinates are expressed in the:

```text
map
```

coordinate frame.

Nav2 processes the goal and generates the robot motion commands.

The navigation chain can be simplified as:

```text
ROS_send_goal
    |
    v
PoseStamped
    |
    v
/goal_pose
    |
    v
Nav2
    |
    v
/cmd_vel
    |
    v
TurtleBot3
```

# Important ROS2 Topics

Useful topics for testing and debugging:

```bash
ros2 topic echo /goal_pose
```

```bash
ros2 topic echo /cmd_vel
```

```bash
ros2 topic echo /odom
```

```bash
ros2 topic echo /scan
```

Check topic information with:

```bash
ros2 topic info /goal_pose -v
```

# Project Structure

```text
chat2robot_k/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yaml
│
└── ros2_ws/
    └── src/
        └── turtlebot3_full_bringup/
            ├── launch/
            │   └── full_bringup.launch.py
            ├── maps/
            ├── config/
            ├── rviz/
            ├── worlds/
            └── scripts/
                ├── streamlit_app.py
                ├── chatbot.py
                ├── rag.py
                ├── ros_tools.py
                └── Angabe.tex
```

# Main Files

## `streamlit_app.py`

Provides the web-based chat interface.

## `chatbot.py`

Contains the main chatbot logic, LLM configuration, RAG integration, chat history and agent executor.

## `rag.py`

Loads the knowledge base, performs chunking, creates embeddings and builds the FAISS vector store.

## `ros_tools.py`

Contains the ROS2 publisher and the LangChain tool used to send navigation goals.

## `Angabe.tex`

Contains the knowledge base used by RAG, including the predefined robot target poses.

## `full_bringup.launch.py`

Starts the TurtleBot3 simulation environment and the required ROS2 navigation components.

# Docker

The project uses Docker to provide a reproducible ROS2 environment.

The Docker container is named:

```text
ros2k
```

The ROS2 workspace from the host is mounted into the container:

```text
../ros2_ws -> /workspace/ros2_ws
```

The container uses host networking to simplify ROS2 communication:

```yaml
network_mode: host
```

# Technologies

- ROS2 Humble
- TurtleBot3 Burger
- Gazebo
- RViz
- Nav2
- AMCL
- Python
- Streamlit
- LangChain
- Google Gemini
- Google Generative AI Embeddings
- FAISS
- Docker
- Docker Compose

# Notes

The current implementation is a proof of concept.

The chatbot sends navigation goals to ROS2, but it does not currently wait for a Nav2 navigation result before issuing another goal.

For a more robust implementation, the `/goal_pose` topic interface could be replaced by a Nav2 `NavigateToPose` Action Client. This would allow the system to receive feedback, detect successful or failed navigation and support sequential navigation goals more reliably.

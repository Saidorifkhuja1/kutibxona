#!/bin/bash

R='\033[0;31m'
G='\033[0;32m'
NOCOLOR='\033[0m'

# Function to run docker compose commands
run_docker() {
    project_dir=$1
    service_name=$2

    cd "/srv/oson_test_project" || { echo -e "${R}Failed to change directory${NOCOLOR}"; exit 1; }
    sleep 1

    if echo "$SUDO_PASSWORD" | sudo -S docker compose -f docker-compose.yml down --remove-orphans $service_name; then
        echo -e "${G}docker compose down success${NOCOLOR}"
        if echo "$SUDO_PASSWORD" | sudo -S docker compose -f docker-compose.yml up -d $service_name; then
            echo -e "${G}docker compose up -d success${NOCOLOR}"
        else
            echo -e "${R}error docker compose up -d.${NOCOLOR}"
            exit 130
        fi
    else
        echo -e "${R}error sudo docker compose down${NOCOLOR}"
        exit 130
    fi
}

# Run the kutubxona-backend project
run_docker "online_library" "web"

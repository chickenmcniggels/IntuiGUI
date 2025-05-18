#!/bin/bash

# Log file for recording activities
LOG_FILE="/home/cnc/deployment_scripts/update_log.txt"

# Function to log messages
log_message() {
    echo "$(date): $1" | tee -a $LOG_FILE
}

# Create log directory if it doesn't exist
mkdir -p /home/cnc/deployment_scripts

# Repository details
REPO_URL="https://github.com/chickenmcniggels/IntuiGUI.git"
LOCAL_REPO="/home/cnc/deployment_scripts/IntuiGUI"

# Deployment paths
CONFIG_DEST="/home/cnc/linuxcnc/configs/IntuiGUI_Config/"
SCREEN_DEST="/usr/share/qtvcp/screens/IntuiGUI/"
WIDGETS_DEST="/usr/lib/python3/dist-packages/qtvcp/widgets"

# Function to handle errors
handle_error() {
    log_message "ERROR: $1"
    # Send notification if needed
    exit 1
}

# Ensure destination directories exist
mkdir -p $CONFIG_DEST || handle_error "Could not create config destination directory"
# The other directories should be system directories and already exist

# Check if repository exists locally
if [ -d "$LOCAL_REPO" ]; then
    # Repository exists, pull updates
    log_message "Pulling updates from repository..."
    cd $LOCAL_REPO || handle_error "Could not change to repository directory"
    
    # Fetch before pull to check for remote changes
    git fetch origin
    
    # Check if there are changes to pull
    LOCAL_SHA=$(git rev-parse HEAD)
    REMOTE_SHA=$(git rev-parse origin/main)
    
    if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
        log_message "Changes detected, pulling updates..."
        git pull origin main || handle_error "Error pulling repository"
        log_message "Repository updated successfully."
    else
        log_message "No changes detected in repository. Continuing to verify deployment..."
    fi
else
    # Repository doesn't exist, clone it
    log_message "Cloning repository..."
    git clone $REPO_URL $LOCAL_REPO || handle_error "Error cloning repository"
    cd $LOCAL_REPO || handle_error "Could not change to repository directory"
fi

# Copy files to their respective destinations
log_message "Copying files to their destinations..."

# IntuiGUI_Config
if [ -d "$LOCAL_REPO/IntuiGUI_Config" ]; then
    log_message "Copying IntuiGUI_Config files..."
    sudo cp -r $LOCAL_REPO/IntuiGUI_Config/* $CONFIG_DEST || handle_error "Failed to copy config files"
fi

# IntuiGUI screens
if [ -d "$LOCAL_REPO/IntuiGUI" ]; then
    log_message "Copying IntuiGUI screen files..."
    sudo cp -r $LOCAL_REPO/IntuiGUI/* $SCREEN_DEST || handle_error "Failed to copy screen files"
fi

# Widgets
if [ -d "$LOCAL_REPO/widgets" ]; then
    log_message "Copying widget files..."
    sudo cp -r $LOCAL_REPO/widgets/* $WIDGETS_DEST || handle_error "Failed to copy widget files"
fi

# Set correct permissions
log_message "Setting correct permissions..."
sudo chown -R cnc:cnc $CONFIG_DEST
sudo chmod -R 755 $SCREEN_DEST $WIDGETS_DEST

log_message "Update completed successfully." 
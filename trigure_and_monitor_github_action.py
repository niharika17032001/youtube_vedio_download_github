from time import sleep

import requests
import time

import ImportantVariables
import crediantials


def trigger_workflow(token, owner, repo, workflow_file, branch="main"):
    """Triggers a GitHub Actions workflow in another repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    data = {"ref": branch}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 204:
        print(f"✅ Successfully triggered workflow '{workflow_file}' in {owner}/{repo}")
        return True
    else:
        print(f"❌ Failed to trigger workflow: {response.json()}")
        return False

def get_latest_run_id(token, owner, repo, workflow_file):
    """Fetches the latest workflow run ID dynamically."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/runs"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        runs = response.json().get("workflow_runs", [])
        if runs:
            latest_run_id = runs[0]["id"]  # Get the most recent workflow run ID
            print(f"✅ Found latest workflow run ID: {latest_run_id}")
            return latest_run_id
        else:
            print("⚠️ No workflow runs found.")
    else:
        print(f"❌ Failed to get workflow runs: {response.json()}")
    return None

def wait_for_workflow_completion(token, owner, repo, run_id, check_interval=10):
    """Waits for the triggered workflow to complete before continuing."""
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            status = response.json().get("status", "")
            print(f"🔄 Workflow Status: {status}")
            if status in ["completed", "failure", "cancelled"]:
                print("✅ Workflow finished. Proceeding with the main process.")
                break
        else:
            print("⚠️ Failed to fetch workflow status.")
            break
        time.sleep(check_interval)

def main():

    GITHUB_TOKEN = crediantials.GITHUB_TOKEN  # Replace with your token
    TRIGGER_REPO_OWNER =ImportantVariables.GITHUB_OWNER
    TRIGGER_REPO_NAME = ImportantVariables.GITHUB_google_log_in_REPO
    WORKFLOW_FILE = ImportantVariables.GITHUB_WORKFLOW_FILE # Change to the actual workflow filename
    BRANCH =ImportantVariables.GITHUB_BRANCH


    # # Step 2: Trigger the workflow in another repository
    if trigger_workflow(GITHUB_TOKEN, TRIGGER_REPO_OWNER, TRIGGER_REPO_NAME, WORKFLOW_FILE, BRANCH):
        sleep(5)
        print("✅ Fetching the latest workflow run ID...")
        RUN_ID = get_latest_run_id(GITHUB_TOKEN, TRIGGER_REPO_OWNER, TRIGGER_REPO_NAME, WORKFLOW_FILE)

        if RUN_ID:
            print("✅ Waiting for the triggered workflow to complete...")
            wait_for_workflow_completion(GITHUB_TOKEN, TRIGGER_REPO_OWNER, TRIGGER_REPO_NAME, RUN_ID)


    # Step 3: Continue with the main process
    print("🚀 Main process continues after triggered workflow is complete!")



# Example Usage:
if __name__ == "__main__":
    main()
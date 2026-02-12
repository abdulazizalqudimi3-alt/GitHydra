(function() {
    const vscode = acquireVsCodeApi();

    const serverStatus = document.getElementById('server-status');
    const btnStart = document.getElementById('btn-start');
    const btnStop = document.getElementById('btn-stop');
    const linkDashboard = document.getElementById('link-dashboard');
    const gitInfo = document.getElementById('git-info');
    const currentBranch = document.getElementById('current-branch');
    const stagedList = document.getElementById('staged-list');
    const unstagedList = document.getElementById('unstaged-list');
    const commitMsg = document.getElementById('commit-msg');
    const btnCommit = document.getElementById('btn-commit');

    // Tab switching logic
    document.querySelectorAll('.tab-item').forEach(tab => {
        tab.addEventListener('click', () => {
            // Update tab headers
            document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update tab contents
            const target = tab.getAttribute('data-tab');
            if (target === 'staged') {
                stagedList.classList.remove('hidden');
                unstagedList.classList.add('hidden');
            } else {
                stagedList.classList.add('hidden');
                unstagedList.classList.remove('hidden');
            }
        });
    });

    btnStart.addEventListener('click', () => {
        vscode.postMessage({ type: 'startServer' });
    });

    btnStop.addEventListener('click', () => {
        vscode.postMessage({ type: 'stopServer' });
    });

    btnCommit.addEventListener('click', () => {
        const message = commitMsg.value.trim();
        if (message) {
            vscode.postMessage({ type: 'gitOp', op: 'commit', params: { message } });
            commitMsg.value = '';
        }
    });

    linkDashboard.addEventListener('click', (e) => {
        e.preventDefault();
        vscode.postMessage({ type: 'openDashboard' });
    });

    window.addEventListener('message', event => {
        const message = event.data;
        switch (message.type) {
            case 'updateState':
                updateUI(message.isRunning, message.url, message.gitStatus);
                break;
        }
    });

    function updateUI(isRunning, url, gitStatus) {
        if (isRunning) {
            serverStatus.textContent = 'Running';
            serverStatus.className = 'status-badge running';
            btnStart.classList.add('hidden');
            btnStop.classList.remove('hidden');
            linkDashboard.classList.remove('hidden');

            if (gitStatus) {
                gitInfo.classList.remove('hidden');
                currentBranch.textContent = gitStatus.branch;

                renderFileList(stagedList, gitStatus.staged, 'unstage');
                renderFileList(unstagedList, gitStatus.unstaged, 'stage');
            }
        } else {
            serverStatus.textContent = 'Stopped';
            serverStatus.className = 'status-badge stopped';
            btnStart.classList.remove('hidden');
            btnStop.classList.add('hidden');
            linkDashboard.classList.add('hidden');
            gitInfo.classList.add('hidden');
        }
    }

    function renderFileList(container, files, action) {
        container.innerHTML = '';
        if (!files || files.length === 0) {
            container.innerHTML = '<div class="empty-msg">No files</div>';
            return;
        }

        files.forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-item';

            const name = document.createElement('span');
            name.textContent = file;
            name.className = 'file-name';

            const btn = document.createElement('button');
            btn.className = 'action-btn';
            btn.textContent = action === 'stage' ? '+' : '-';
            btn.title = action === 'stage' ? 'Stage' : 'Unstage';
            btn.addEventListener('click', () => {
                vscode.postMessage({ type: 'gitOp', op: action, params: { files: [file] } });
            });

            item.appendChild(name);
            item.appendChild(btn);
            container.appendChild(item);
        });
    }

    // Initial refresh
    vscode.postMessage({ type: 'refresh' });
}());

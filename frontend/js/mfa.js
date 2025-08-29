// MFA-specific functionality for the frontend

// MFA State Management
let mfaToken = null;
let mfaSetupInProgress = false;

// MFA Setup Flow
async function initiateMfaSetup() {
  try {
    showLoading(true, 'Initiating MFA setup...');

    const response = await apiCall('/auth/mfa/setup/initiate', {
      method: 'POST',
    });

    return response;
  } catch (error) {
    console.error('Error initiating MFA setup:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

async function completeMfaSetup(secretKey, verificationCode) {
  try {
    showLoading(true, 'Completing MFA setup...');

    const response = await apiCall('/auth/mfa/setup/complete', {
      method: 'POST',
      body: JSON.stringify({
        secret_key: secretKey,
        verification_code: verificationCode,
      }),
    });

    return response;
  } catch (error) {
    console.error('Error completing MFA setup:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

// MFA Verification (Login Flow)
async function verifyMfaCode(mfaCode, mfaToken) {
  try {
    showLoading(true, 'Verifying MFA code...');

    const response = await apiCall('/auth/mfa/verify', {
      method: 'POST',
      body: JSON.stringify({
        mfa_code: mfaCode,
        mfa_token: mfaToken,
      }),
    });

    return response;
  } catch (error) {
    console.error('Error verifying MFA code:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

// MFA Status Check
async function getMfaStatus() {
  try {
    const response = await apiCall('/auth/mfa/status', {
      method: 'GET',
    });

    return response;
  } catch (error) {
    console.error('Error getting MFA status:', error);
    throw error;
  }
}

// Disable MFA
async function disableMfa(password, mfaCode) {
  try {
    showLoading(true, 'Disabling MFA...');

    const response = await apiCall('/auth/mfa/disable', {
      method: 'POST',
      body: JSON.stringify({
        password: password,
        mfa_code: mfaCode,
      }),
    });

    return response;
  } catch (error) {
    console.error('Error disabling MFA:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

// Generate new backup codes
async function regenerateBackupCodes() {
  try {
    showLoading(true, 'Generating new backup codes...');

    const response = await apiCall('/auth/mfa/backup-codes/regenerate', {
      method: 'POST',
    });

    return response;
  } catch (error) {
    console.error('Error regenerating backup codes:', error);
    throw error;
  } finally {
    showLoading(false);
  }
}

// UI Helper Functions for MFA

function showMfaVerificationModal(mfaToken) {
  // Store the MFA token for verification
  window.mfaToken = mfaToken;

  // Create MFA verification modal
  const modalHtml = `
    <div class="modal fade" id="mfaVerificationModal" tabindex="-1" aria-labelledby="mfaVerificationModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="mfaVerificationModalLabel">
                        <i class="fas fa-shield-alt me-2"></i>Two-Factor Authentication
                    </h5>
                </div>
                <div class="modal-body">
                    <div class="text-center mb-4">
                        <div class="mb-3">
                            <i class="fas fa-mobile-alt fa-3x text-primary mb-3"></i>
                        </div>
                        <p class="text-muted">
                            Please enter the 6-digit code from your authenticator app or use a backup code.
                        </p>
                    </div>
                    
                    <form id="mfaVerificationForm">
                        <div class="mb-3">
                            <label for="mfaCode" class="form-label">Authentication Code</label>
                            <input type="text" 
                                   class="form-control form-control-lg text-center" 
                                   id="mfaCode" 
                                   placeholder="000000"
                                   maxlength="8"
                                   pattern="[0-9A-Z]{6,8}"
                                   autocomplete="one-time-code"
                                   required>
                            <div class="form-text">
                                Enter the 6-digit code from your app or an 8-character backup code
                            </div>
                            <div class="invalid-feedback" id="mfaCodeError"></div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-check me-2"></i>Verify Code
                            </button>
                        </div>
                    </form>
                    
                    <div class="text-center mt-3">
                        <small class="text-muted">
                            Lost your device? Use one of your backup codes instead.
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>`;

  // Remove existing modal if any
  const existingModal = document.getElementById('mfaVerificationModal');
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to DOM
  document.body.insertAdjacentHTML('beforeend', modalHtml);

  // Initialize modal
  const modal = new bootstrap.Modal(
    document.getElementById('mfaVerificationModal')
  );

  // Handle form submission
  const form = document.getElementById('mfaVerificationForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleMfaVerification();
  });

  // Auto-format MFA code input
  const mfaCodeInput = document.getElementById('mfaCode');
  mfaCodeInput.addEventListener('input', (e) => {
    let value = e.target.value.replace(/[^0-9A-Z]/g, '');
    e.target.value = value;

    // Auto-submit when 6 or 8 characters are entered
    if (value.length === 6 || value.length === 8) {
      setTimeout(() => {
        form.dispatchEvent(new Event('submit'));
      }, 300);
    }
  });

  // Show modal and focus input
  modal.show();
  setTimeout(() => {
    mfaCodeInput.focus();
  }, 500);

  return modal;
}

async function handleMfaVerification() {
  try {
    const mfaCode = document.getElementById('mfaCode').value.trim();
    const mfaToken = window.mfaToken;

    if (!mfaCode) {
      setFieldError('mfaCode', 'Please enter the authentication code');
      return;
    }

    if (mfaCode.length !== 6 && mfaCode.length !== 8) {
      setFieldError('mfaCode', 'Code must be 6 digits or 8 characters');
      return;
    }

    // Clear any previous errors
    clearFieldError('mfaCode');

    // Verify MFA code
    const response = await verifyMfaCode(mfaCode, mfaToken);

    // Save the new access token
    saveAuthToken(response.access_token);

    // Close modal
    const modal = bootstrap.Modal.getInstance(
      document.getElementById('mfaVerificationModal')
    );
    modal.hide();

    // Get user profile and redirect
    const profile = await apiCall('/me', { method: 'GET' });

    showAlert('Login successful! Redirecting...', 'success');

    setTimeout(() => {
      if (profile.role === 'admin' || profile.role === 'super_admin') {
        window.location.href = 'admin-dashboard.html';
      } else {
        window.location.href = 'client-dashboard.html';
      }
    }, 1000);
  } catch (error) {
    let errorMessage = 'Invalid authentication code. Please try again.';

    if (error.message.includes('expired')) {
      errorMessage = 'Authentication session expired. Please log in again.';
      // Close modal and redirect to login
      const modal = bootstrap.Modal.getInstance(
        document.getElementById('mfaVerificationModal')
      );
      modal.hide();
      setTimeout(() => {
        window.location.href = 'login.html';
      }, 2000);
    } else if (error.message.includes('Invalid MFA code')) {
      errorMessage =
        'Invalid code. Please check your authenticator app and try again.';
    }

    setFieldError('mfaCode', errorMessage);

    // Clear the input and refocus
    const mfaCodeInput = document.getElementById('mfaCode');
    mfaCodeInput.value = '';
    mfaCodeInput.focus();
  }
}

function showMfaSetupModal() {
  // Create MFA setup modal
  const modalHtml = `
    <div class="modal fade" id="mfaSetupModal" tabindex="-1" aria-labelledby="mfaSetupModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="mfaSetupModalLabel">
                        <i class="fas fa-shield-alt me-2"></i>Setup Two-Factor Authentication
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <!-- Step 1: QR Code Display -->
                    <div id="mfaStep1" class="mfa-step">
                        <div class="text-center mb-4">
                            <h6 class="fw-bold">Step 1: Scan QR Code</h6>
                            <p class="text-muted">
                                Use your authenticator app (Google Authenticator, Authy, etc.) to scan this QR code:
                            </p>
                        </div>
                        
                        <div class="text-center mb-4">
                            <div id="qrCodeContainer" class="d-inline-block p-3 border rounded">
                                <div class="spinner-border" role="status">
                                    <span class="visually-hidden">Loading QR code...</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Manual Entry:</strong> If you can't scan the QR code, 
                            you can manually enter this secret key in your app: 
                            <code id="secretKeyDisplay">Loading...</code>
                        </div>
                        
                        <div class="d-grid">
                            <button type="button" class="btn btn-primary" onclick="showMfaVerificationStep()">
                                <i class="fas fa-arrow-right me-2"></i>Next: Verify Setup
                            </button>
                        </div>
                    </div>
                    
                    <!-- Step 2: Verification -->
                    <div id="mfaStep2" class="mfa-step d-none">
                        <div class="text-center mb-4">
                            <h6 class="fw-bold">Step 2: Verify Your Setup</h6>
                            <p class="text-muted">
                                Enter the 6-digit code from your authenticator app to complete setup:
                            </p>
                        </div>
                        
                        <form id="mfaSetupForm">
                            <div class="mb-3">
                                <label for="setupVerificationCode" class="form-label">Verification Code</label>
                                <input type="text" 
                                       class="form-control form-control-lg text-center" 
                                       id="setupVerificationCode" 
                                       placeholder="000000"
                                       maxlength="6"
                                       pattern="[0-9]{6}"
                                       autocomplete="one-time-code"
                                       required>
                                <div class="form-text">
                                    Enter the 6-digit code shown in your authenticator app
                                </div>
                                <div class="invalid-feedback" id="setupVerificationCodeError"></div>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-success btn-lg">
                                    <i class="fas fa-check me-2"></i>Complete MFA Setup
                                </button>
                                <button type="button" class="btn btn-outline-secondary" onclick="showMfaQrStep()">
                                    <i class="fas fa-arrow-left me-2"></i>Back to QR Code
                                </button>
                            </div>
                        </form>
                    </div>
                    
                    <!-- Step 3: Success with Backup Codes -->
                    <div id="mfaStep3" class="mfa-step d-none">
                        <div class="text-center mb-4">
                            <div class="text-success mb-3">
                                <i class="fas fa-check-circle fa-3x"></i>
                            </div>
                            <h6 class="fw-bold text-success">MFA Setup Complete!</h6>
                            <p class="text-muted">
                                Your account is now protected with two-factor authentication.
                            </p>
                        </div>
                        
                        <div class="alert alert-warning">
                            <h6 class="alert-heading">
                                <i class="fas fa-key me-2"></i>Important: Save Your Backup Codes
                            </h6>
                            <p class="mb-2">
                                Store these backup codes in a safe place. You can use them to access your account if you lose your phone:
                            </p>
                            <div id="backupCodesList" class="font-monospace small bg-light p-2 rounded">
                                <!-- Backup codes will be inserted here -->
                            </div>
                            <div class="mt-2">
                                <button type="button" class="btn btn-sm btn-outline-primary" onclick="downloadBackupCodes()">
                                    <i class="fas fa-download me-1"></i>Download Codes
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-secondary ms-2" onclick="printBackupCodes()">
                                    <i class="fas fa-print me-1"></i>Print Codes
                                </button>
                            </div>
                        </div>
                        
                        <div class="d-grid">
                            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">
                                <i class="fas fa-check me-2"></i>Finish
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;

  // Remove existing modal if any
  const existingModal = document.getElementById('mfaSetupModal');
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to DOM
  document.body.insertAdjacentHTML('beforeend', modalHtml);

  // Initialize modal
  const modal = new bootstrap.Modal(document.getElementById('mfaSetupModal'));

  // Load QR code and setup
  initializeMfaSetup();

  // Show modal
  modal.show();

  return modal;
}

async function initializeMfaSetup() {
  try {
    const setupData = await initiateMfaSetup();

    // Display QR code
    const qrContainer = document.getElementById('qrCodeContainer');
    qrContainer.innerHTML = `<img src="data:image/png;base64,${setupData.qr_code}" alt="MFA QR Code" style="max-width: 200px;">`;

    // Display secret key
    const secretDisplay = document.getElementById('secretKeyDisplay');
    secretDisplay.textContent = setupData.secret_key;

    // Store secret for completion
    window.mfaSetupSecret = setupData.secret_key;

    // Setup form handler
    const form = document.getElementById('mfaSetupForm');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleMfaSetupCompletion();
    });
  } catch (error) {
    console.error('Error initializing MFA setup:', error);
    showAlert('Failed to initialize MFA setup. Please try again.', 'danger');
  }
}

async function handleMfaSetupCompletion() {
  try {
    const verificationCode = document
      .getElementById('setupVerificationCode')
      .value.trim();
    const secretKey = window.mfaSetupSecret;

    if (!verificationCode) {
      setFieldError(
        'setupVerificationCode',
        'Please enter the verification code'
      );
      return;
    }

    if (verificationCode.length !== 6) {
      setFieldError('setupVerificationCode', 'Code must be 6 digits');
      return;
    }

    clearFieldError('setupVerificationCode');

    // Complete MFA setup
    const response = await completeMfaSetup(secretKey, verificationCode);

    // Show success step with backup codes
    showMfaSuccessStep(response.backup_codes);
  } catch (error) {
    console.error('Error completing MFA setup:', error);
    let errorMessage = 'Invalid verification code. Please try again.';

    if (error.message.includes('Invalid verification code')) {
      errorMessage =
        'Invalid code. Please check your authenticator app and try again.';
    }

    setFieldError('setupVerificationCode', errorMessage);

    // Clear input and refocus
    const input = document.getElementById('setupVerificationCode');
    input.value = '';
    input.focus();
  }
}

function showMfaQrStep() {
  document.getElementById('mfaStep1').classList.remove('d-none');
  document.getElementById('mfaStep2').classList.add('d-none');
  document.getElementById('mfaStep3').classList.add('d-none');
}

function showMfaVerificationStep() {
  document.getElementById('mfaStep1').classList.add('d-none');
  document.getElementById('mfaStep2').classList.remove('d-none');
  document.getElementById('mfaStep3').classList.add('d-none');

  // Focus on verification input
  setTimeout(() => {
    document.getElementById('setupVerificationCode').focus();
  }, 300);
}

function showMfaSuccessStep(backupCodes) {
  document.getElementById('mfaStep1').classList.add('d-none');
  document.getElementById('mfaStep2').classList.add('d-none');
  document.getElementById('mfaStep3').classList.remove('d-none');

  // Display backup codes
  const codesList = document.getElementById('backupCodesList');
  const codesHtml = backupCodes
    .map((code, index) => `<div>${index + 1}. ${code}</div>`)
    .join('');
  codesList.innerHTML = codesHtml;

  // Store codes for download/print
  window.mfaBackupCodes = backupCodes;
}

function downloadBackupCodes() {
  const codes = window.mfaBackupCodes;
  if (!codes) return;

  const content = `Two-Factor Authentication Backup Codes
Generated: ${new Date().toLocaleDateString()}

IMPORTANT: Store these codes in a safe place. Each code can only be used once.

${codes.map((code, index) => `${index + 1}. ${code}`).join('\n')}

If you lose access to your authenticator app, you can use these codes to log in.
After using a code, it will no longer be valid.`;

  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'mfa-backup-codes.txt';
  link.click();
  URL.revokeObjectURL(url);
}

function printBackupCodes() {
  const codes = window.mfaBackupCodes;
  if (!codes) return;

  const printWindow = window.open('', '', 'width=600,height=400');
  printWindow.document.write(`
        <html>
        <head>
            <title>MFA Backup Codes</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .codes { font-family: monospace; font-size: 14px; line-height: 1.8; }
                .footer { margin-top: 30px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Two-Factor Authentication Backup Codes</h2>
                <p>Generated: ${new Date().toLocaleDateString()}</p>
            </div>
            
            <div class="warning">
                <strong>IMPORTANT:</strong> Store these codes in a safe place. Each code can only be used once.
            </div>
            
            <div class="codes">
                ${codes
                  .map((code, index) => `<div>${index + 1}. ${code}</div>`)
                  .join('')}
            </div>
            
            <div class="footer">
                <p>If you lose access to your authenticator app, you can use these codes to log in.</p>
                <p>After using a code, it will no longer be valid.</p>
            </div>
        </body>
        </html>
    `);
  printWindow.document.close();
  printWindow.print();
}

// Utility function to format MFA input
function formatMfaInput(input) {
  const value = input.value.replace(/[^0-9A-Z]/g, '');
  input.value = value;
  return value;
}

// Check if MFA is required for current user
async function checkMfaRequired() {
  try {
    const token = getAuthToken();
    if (!token) return false;

    const status = await getMfaStatus();
    return !status.enabled; // Return true if MFA is not enabled (setup required)
  } catch (error) {
    console.log('Could not check MFA status:', error);
    return false;
  }
}

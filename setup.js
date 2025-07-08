#!/usr/bin/env node
/**
 * Setup script for Guinée Makiti E-commerce Platform
 * Node.js version to work in WebContainer environment
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function runCommand(command, description) {
    console.log(`\n🔄 ${description}...`);
    try {
        execSync(command, { stdio: 'inherit' });
        console.log(`✅ ${description} completed successfully`);
        return true;
    } catch (error) {
        console.log(`❌ Error in ${description}: ${error.message}`);
        return false;
    }
}

function checkPython() {
    try {
        execSync('python3 --version', { stdio: 'pipe' });
        console.log('✅ Python3 found');
        return true;
    } catch {
        console.log('❌ Python3 not found');
        return false;
    }
}

function setupEnvFile() {
    if (!fs.existsSync('.env')) {
        if (fs.existsSync('.env.example')) {
            fs.copyFileSync('.env.example', '.env');
            console.log('✅ Created .env file from .env.example');
            console.log('⚠️  Please edit .env file with your actual configuration');
        } else {
            const envContent = `SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Payment Settings (optional)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
`;
            fs.writeFileSync('.env', envContent);
            console.log('✅ Created basic .env file');
        }
    } else {
        console.log('✅ .env file already exists');
    }
    return true;
}

function createMediaDirectories() {
    const directories = [
        'media',
        'media/products',
        'media/profiles',
        'media/shops',
        'media/reviews',
        'static/images',
        'static/logos'
    ];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
    
    console.log('✅ Created media directories');
    return true;
}

function installPythonDependencies() {
    if (!fs.existsSync('requirements.txt')) {
        console.log('❌ requirements.txt not found');
        return false;
    }
    
    // Try to install with pip3 directly (no virtual environment in WebContainer)
    return runCommand('pip3 install -r requirements.txt --user', 'Installing Python packages');
}

function setupDatabase() {
    const commands = [
        ['python3 manage.py makemigrations', 'Creating migrations'],
        ['python3 manage.py migrate', 'Running migrations'],
    ];
    
    for (const [command, description] of commands) {
        if (!runCommand(command, description)) {
            return false;
        }
    }
    return true;
}

function main() {
    console.log('🚀 Setting up Guinée Makiti E-commerce Platform');
    console.log('=' .repeat(50));
    
    // Check prerequisites
    if (!checkPython()) {
        console.log('❌ Python3 is required but not found');
        return false;
    }
    
    // Setup steps
    const steps = [
        [setupEnvFile, 'Environment Configuration'],
        [createMediaDirectories, 'Directory Structure'],
        [installPythonDependencies, 'Package Installation'],
        [setupDatabase, 'Database Setup'],
    ];
    
    for (const [stepFunc, stepName] of steps) {
        if (!stepFunc()) {
            console.log(`❌ Setup failed at: ${stepName}`);
            return false;
        }
    }
    
    console.log('\n' + '='.repeat(50));
    console.log('🎉 Setup completed successfully!');
    console.log('\nNext steps:');
    console.log('1. Edit the .env file with your configuration');
    console.log('2. Run the development server:');
    console.log('   python3 manage.py runserver');
    console.log('3. Open http://127.0.0.1:8000 in your browser');
    console.log('\n📧 Admin panel: http://127.0.0.1:8000/admin/');
    console.log('🛍️  Main site: http://127.0.0.1:8000/');
    
    return true;
}

if (require.main === module) {
    main();
}
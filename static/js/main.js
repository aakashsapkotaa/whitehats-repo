// ===== EduHub Quote Database =====
const quotes = [
    { text: "Knowledge is a treasure, but practice is the key to it.", author: "Lao Tzu" },
    { text: "The beautiful thing about learning is that no one can take it away from you.", author: "B.B. King" },
    { text: "Education is the passport to the future.", author: "Malcolm X" },
    { text: "Share your knowledge. It is a way to achieve immortality.", author: "Dalai Lama" },
    { text: "The mind is not a vessel to be filled, but a fire to be kindled.", author: "Plutarch" },
    { text: "Alone we can do so little; together we can do so much.", author: "Helen Keller" },
    { text: "Wisdom is not a product of schooling but of the lifelong attempt to acquire it.", author: "Albert Einstein" },
    { text: "Teaching is the greatest act of optimism.", author: "Colleen Wilcox" },
    { text: "He who learns but does not think, is lost.", author: "Confucius" },
    { text: "Your attitude, not your aptitude, will determine your altitude.", author: "Zig Ziglar" },
    { text: "Learning never exhausts the mind.", author: "Leonardo da Vinci" },
    { text: "The best way to predict your future is to create it.", author: "Peter Drucker" },
    { text: "Education breeds confidence. Confidence breeds hope.", author: "Confucius" },
    { text: "Live as if you were to die tomorrow. Learn as if you were to live forever.", author: "Mahatma Gandhi" },
    { text: "The more that you read, the more things you will know.", author: "Dr. Seuss" },
    { text: "Change is the end result of all true learning.", author: "Leo Buscaglia" },
    { text: "Knowledge is power. Information is liberating.", author: "Kofi Annan" },
    { text: "Develop a passion for learning. If you do, you will never cease to grow.", author: "Anthony D'Angelo" }
];

// ===== State Management =====
let currentUser = {
    avatar: null,
    name: null,
    email: null
};

// ===== Navigation Functions =====
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden-section');
        section.classList.remove('fade-in');
    });
    
    // Show target section
    const target = document.getElementById(sectionId);
    if (target) {
        target.classList.remove('hidden-section');
        target.classList.add('fade-in');
    }
}

function switchSection(hideId, showId) {
    const hideEl = document.getElementById(hideId);
    const showEl = document.getElementById(showId);
    
    if (!hideEl || !showEl) return;

    hideEl.classList.add('fade-out');
    
    setTimeout(() => {
        hideEl.classList.add('hidden-section');
        hideEl.classList.remove('fade-out');
        
        showEl.classList.remove('hidden-section');
        showEl.classList.add('fade-in');
    }, 500);
}

// ===== Login Handlers =====
function handleSocialLogin(provider) {
    console.log(`Initiating ${provider} login...`);
    const btn = event.currentTarget;
    const originalHTML = btn.innerHTML;
    
    // Show loading state
    btn.innerHTML = `<i class="fas fa-circle-notch fa-spin"></i> Connecting to ${provider}...`;
    btn.disabled = true;
    
    // Simulate OAuth redirect
    setTimeout(() => {
        // Mock successful login
        currentUser.name = provider + "User";
        currentUser.email = "user@" + provider.toLowerCase() + ".com";
        
        btn.innerHTML = originalHTML;
        btn.disabled = false;
        
        // Move to avatar setup
        switchSection('login-section', 'avatar-section');
    }, 2000);
}

function handleManualLogin(event) {
    event.preventDefault();
    
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;
    const btn = form.querySelector('button[type="submit"]');
    
    // Validate
    if (!email || !password) {
        alert("Please fill in all fields");
        return;
    }
    
    // Show loading
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-circle-notch fa-spin mr-2"></i> Signing In...`;
    btn.disabled = true;
    
    setTimeout(() => {
        currentUser.email = email;
        currentUser.name = email.split('@')[0];
        
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        switchSection('login-section', 'avatar-section');
    }, 1500);
}

// ===== Avatar Upload =====
function previewImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert("Please upload an image file");
        return;
    }
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert("File size must be less than 5MB");
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        currentUser.avatar = e.target.result;
        
        const preview = document.getElementById('avatar-preview');
        preview.innerHTML = `<img src="${currentUser.avatar}" alt="Avatar">`;
        
        const fileNameEl = document.getElementById('file-name');
        fileNameEl.textContent = file.name;
        fileNameEl.classList.add('text-primary');
    };
    reader.readAsDataURL(file);
}

function triggerFileInput() {
    document.getElementById('file-input').click();
}

function proceedToLoading() {
    // If no avatar selected, generate default
    if (!currentUser.avatar) {
        const name = currentUser.name || "User";
        currentUser.avatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=0F5257&color=55D6BE&size=128`;
    }
    
    // Update dashboard avatar
    const navAvatar = document.getElementById('nav-avatar');
    if (navAvatar) {
        navAvatar.src = currentUser.avatar;
        navAvatar.classList.remove('hidden');
    }
    
    // Update welcome message
    const welcomeName = document.getElementById('welcome-name');
    if (welcomeName) {
        welcomeName.textContent = currentUser.name || "Learner";
    }
    
    switchSection('avatar-section', 'loading-section');
    startLoadingSequence();
}

// ===== Loading Screen with Quotes =====
function startLoadingSequence() {
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    
    const textEl = document.getElementById('quote-text');
    const authorEl = document.getElementById('quote-author');
    
    // Reset
    textEl.innerHTML = '';
    authorEl.style.opacity = '0';
    
    // Typewriter effect
    let i = 0;
    const speed = 40;
    
    function typeWriter() {
        if (i < randomQuote.text.length) {
            textEl.innerHTML += randomQuote.text.charAt(i);
            i++;
            setTimeout(typeWriter, speed);
        } else {
            // Show author with delay
            setTimeout(() => {
                authorEl.textContent = `— ${randomQuote.author}`;
                authorEl.style.opacity = '1';
            }, 300);
        }
    }
    
    typeWriter();
    
    // Navigate to dashboard after loading
    setTimeout(() => {
        const loadingSection = document.getElementById('loading-section');
        loadingSection.style.transition = 'opacity 0.8s ease';
        loadingSection.style.opacity = '0';
        
        setTimeout(() => {
            loadingSection.classList.add('hidden-section');
            document.getElementById('dashboard-section').classList.remove('hidden-section');
            document.getElementById('dashboard-section').classList.add('fade-in');
            
            // Reset loading section for next time
            loadingSection.style.opacity = '1';
        }, 800);
    }, 4500);
}

// ===== Drag and Drop =====
function setupDragAndDrop() {
    const dropArea = document.getElementById('drop-area');
    if (!dropArea) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('active'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('active'), false);
    });
    
    dropArea.addEventListener('drop', handleDrop, false);
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        const fileInput = document.getElementById('file-input');
        fileInput.files = files;
        
        // Trigger change event manually
        const event = new Event('change');
        fileInput.dispatchEvent(event);
    }
}

// ===== Initialize =====
document.addEventListener('DOMContentLoaded', function() {
    setupDragAndDrop();
    
    // Check if user is already logged in (mock)
    const isLoggedIn = sessionStorage.getItem('eduhub_logged_in');
    if (isLoggedIn) {
        showSection('dashboard-section');
    } else {
        showSection('login-section');
    }
});

// ===== Utility Functions =====
function logout() {
    sessionStorage.removeItem('eduhub_logged_in');
    currentUser = { avatar: null, name: null, email: null };
    location.reload();
}

function showToast(message, type = 'success') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white font-medium z-50 fade-in ${
        type === 'success' ? 'bg-[#55D6BE] text-[#32292F]' : 'bg-red-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}
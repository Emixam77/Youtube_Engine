let currentTab = 'youtube';
let chatHistory = [
    {role: 'system', text: 'Bonjour ! Je suis votre directeur créatif Gemini. Comment pouvons-nous structurer votre prochaine vidéo aujourd\'hui ? Indiquez-moi votre idée de départ ou votre lien d\'inspiration.'}
];

// Document Elements
const styleList = document.getElementById('styleList');
const projectsGrid = document.getElementById('projectsGrid');
const chatHistoryContainer = document.getElementById('chatHistory');
const chatInput = document.getElementById('chatInput');
const currentTabTitle = document.getElementById('currentTabTitle');

// Modal Elements
const createModal = document.getElementById('createModal');
const openCreateModalBtn = document.getElementById('openCreateModalBtn');
const closeCreateModalBtn = document.getElementById('closeCreateModalBtn');
const createProjectForm = document.getElementById('createProjectForm');

const promptViewerModal = document.getElementById('promptViewerModal');
const closePromptViewerBtn = document.getElementById('closePromptViewerBtn');
const viewerProjTitle = document.getElementById('viewerProjTitle');
const viewerProjFormat = document.getElementById('viewerProjFormat');
const viewerProjStyle = document.getElementById('viewerProjStyle');
const viewerPromptsContainer = document.getElementById('viewerPromptsContainer');

// New Collapsible & Channels Elements
const toggleStylesBtn = document.getElementById('toggleStylesBtn');
const channelsSection = document.getElementById('channelsSection');
const channelsList = document.getElementById('channelsList');
const newChannelInput = document.getElementById('newChannelInput');
const addChannelBtn = document.getElementById('addChannelBtn');

// ⚙️ INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
    loadStyles();
    loadProjects();
    loadChannels();
    setupEventListeners();
});

// Setup Navigation and Actions
function setupEventListeners() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelector('.nav-btn.active').classList.remove('active');
            e.target.classList.add('active');
            currentTab = e.target.getAttribute('data-tab');
            currentTabTitle.innerText = e.target.innerText;
            loadProjects();
            loadChannels();
        });
    });

    toggleStylesBtn.addEventListener('click', () => {
        styleList.classList.toggle('collapsed');
        const icon = toggleStylesBtn.querySelector('.toggle-icon');
        if (styleList.classList.contains('collapsed')) {
            icon.style.transform = 'rotate(-90deg)';
        } else {
            icon.style.transform = 'rotate(0deg)';
        }
    });

    addChannelBtn.addEventListener('click', addChannel);
    newChannelInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') addChannel();
    });

    openCreateModalBtn.addEventListener('click', () => createModal.classList.add('active'));
    closeCreateModalBtn.addEventListener('click', () => createModal.classList.remove('active'));
    closePromptViewerBtn.addEventListener('click', () => promptViewerModal.classList.remove('active'));

    createProjectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('projTitle').value;
        const format = document.getElementById('projFormat').value;
        const style = document.getElementById('projStyle').value;
        const notes = document.getElementById('projNotes').value;

        // Structure proper properties based on Notion schema
        const properties = {
            "Format": { "select": { "name": format } },
            "Statut": { "select": { "name": "💡 Idée" } },
            "Style Visuel / DA": { "rich_text": [{ "text": { "content": style } }] },
            "Notes": { "rich_text": [{ "text": { "content": notes } }] }
        };

        if (currentTab === 'youtube') {
            properties["Titre du Post"] = { "title": [{ "text": { "content": title } }] };
        } else if (currentTab === 'marketing') {
            properties["Titre de la Campagne"] = { "title": [{ "text": { "content": title } }] };
            properties["Branche"] = { "select": { "name": "📱 Social Media" } };
            properties["Objectif"] = { "select": { "name": "🎯 Acquisition" } };
            properties["Plateforme Cible"] = { "select": { "name": "YouTube" } };
        } else {
            properties["Titre du Projet"] = { "title": [{ "text": { "content": title } }] };
        }

        try {
            const response = await fetch('/api/pages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    database_type: currentTab,
                    title: title,
                    properties: properties
                })
            });
            
            if (response.ok) {
                createModal.classList.remove('active');
                createProjectForm.reset();
                loadProjects();
            } else {
                alert("Erreur lors de la synchronisation Notion.");
            }
        } catch (error) {
            console.error(error);
        }
    });
}

// 📂 FETCH PROJECTS FROM NOTION
async function loadProjects() {
    projectsGrid.innerHTML = '<div class="loading">Chargement des données Notion...</div>';
    try {
        const response = await fetch(`/api/databases/${currentTab}/pages`);
        const pages = await response.json();
        projectsGrid.innerHTML = '';
        
        if (pages.length === 0) {
            projectsGrid.innerHTML = '<div class="empty">Aucun projet trouvé.</div>';
            return;
        }

        pages.forEach(page => {
            const titleProp = page.properties["Titre du Post"] || page.properties["Titre de la Campagne"] || page.properties["Titre du Projet"];
            const title = titleProp?.title[0]?.plain_text || "Projet sans titre";
            const format = page.properties["Format"]?.select?.name || "Format non défini";
            const status = page.properties["Statut"]?.select?.name || "💡 Idée";
            const style = page.properties["Style Visuel / DA"]?.rich_text[0]?.plain_text || "DA non définie";
            const notes = page.properties["Notes"]?.rich_text[0]?.plain_text || "";

            let statusClass = 'status-gray';
            if (status.includes('Validation') || status.includes('En cours')) statusClass = 'status-orange';
            if (status.includes('Livré') || status.includes('Publié')) statusClass = 'status-green';

            const card = document.createElement('div');
            card.className = 'project-card';
            card.innerHTML = `
                <div class="badge ${statusClass}">${status}</div>
                <h4>${title}</h4>
                <p><strong>Format</strong> : ${format}</p>
                <p><strong>Style Visuel</strong> : ${style}</p>
                <p>${notes}</p>
            `;
            
            card.addEventListener('click', () => openPromptViewer(title, format, style));
            projectsGrid.appendChild(card);
        });
    } catch (error) {
        projectsGrid.innerHTML = '<div class="error">Erreur de connexion.</div>';
        console.error(error);
    }
}

// 🎨 LOAD COLLAGE STYLES LIBRARIES
async function loadStyles() {
    try {
        const response = await fetch('/api/styles');
        const data = await response.json();
        styleList.innerHTML = '';
        
        data.styles.forEach(style => {
            const item = document.createElement('div');
            item.className = 'style-item';
            item.innerHTML = `
                <div class="style-item-header">
                    <span>Style ${style.id} : ${style.name}</span>
                    <span style="color: ${style.hex === '#FFFFFF' ? '#999' : style.hex}">●</span>
                </div>
                <div class="style-item-desc">${style.desc}</div>
            `;
            
            item.addEventListener('click', () => {
                sendQuickMessage(`Parle-moi du style "${style.name}" et comment l'utiliser pour ma vidéo.`);
            });
            styleList.appendChild(item);
        });
    } catch (error) {
        console.error(error);
    }
}

// 💬 GEMINI CHAT FUNCTIONS
async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    appendMessage('user', text);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: chatHistory
            })
        });
        const data = await response.json();
        
        if (!response.ok) {
            appendMessage('system', `Erreur : ${data.detail || 'Erreur inconnue de l\'API'}`);
            return;
        }
        
        appendMessage('system', data.reply);
        chatHistory.push({role: 'user', text: text});
        chatHistory.push({role: 'system', text: data.reply});
    } catch (error) {
        appendMessage('system', 'Erreur : impossible de contacter le serveur.');
    }
}

function sendQuickMessage(text) {
    chatInput.value = text;
    sendChatMessage();
}

function appendMessage(role, text) {
    const msg = document.createElement('div');
    msg.className = `message ${role}`;
    msg.innerText = text;
    chatHistoryContainer.appendChild(msg);
    chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
}

// 🍿 PROMPT GENERATOR VIEW
function openPromptViewer(title, format, style) {
    viewerProjTitle.innerText = title;
    viewerProjFormat.innerText = format;
    viewerProjStyle.innerText = `Style : ${style}`;
    
    // Generate dynamic mock BROLL prompts tailored with style and aspect ratio
    const isShort = format.includes('Short') || format.includes('9:16');
    const ratioStr = isShort ? '9:16' : '16:9';
    
    viewerPromptsContainer.innerHTML = `
        <div class="prompt-card">
            <h5>Plan 001 - Hook initial (${ratioStr})</h5>
            <div class="prompt-text">Use the style of "${style}" -- high-contrast editorial diorama, camera flies low between paper cutouts, aspect ratio ${ratioStr}. Paper pops, whoosh. No music, no narration.</div>
            <button class="copy-btn" onclick="copyToClipboard(this)">Copier le prompt</button>
        </div>
        <div class="prompt-card">
            <h5>Plan 002 - Révélation donnée/concept (${ratioStr})</h5>
            <div class="prompt-text">Use the style of "${style}" -- split screen diorama, camera racks focus from foreground element to main bold headline. Accents of color, film grain. Aspect ratio ${ratioStr}. Stamp pop, ticks.</div>
            <button class="copy-btn" onclick="copyToClipboard(this)">Copier le prompt</button>
        </div>
    `;
    
    promptViewerModal.classList.add('active');
}

function copyToClipboard(button) {
    const text = button.previousElementSibling.innerText;
    navigator.clipboard.writeText(text);
    const originalText = button.innerText;
    button.innerText = 'Copié !';
    button.style.background = '#2ed573';
    button.style.borderColor = '#2ed573';
    button.style.color = '#fff';
    setTimeout(() => {
        button.innerText = originalText;
        button.style.background = '';
        button.style.borderColor = '';
        button.style.color = '';
    }, 2000);
}

// 📡 REFERENCE CHANNELS LOGIC
async function loadChannels() {
    if (currentTab !== 'youtube') {
        channelsSection.style.display = 'none';
        return;
    }
    channelsSection.style.display = 'block';
    try {
        const response = await fetch('/api/reference-channels');
        const channels = await response.json();
        channelsList.innerHTML = '';
        
        if (channels.length === 0) {
            channelsList.innerHTML = '<span class="empty-text" style="font-size:12px;color:var(--text-muted);">Aucune chaîne ajoutée.</span>';
            return;
        }

        channels.forEach(ch => {
            const pill = document.createElement('div');
            pill.className = 'channel-pill';
            pill.innerHTML = `
                <span>${ch}</span>
                <span class="channel-delete-btn" onclick="deleteChannel('${encodeURIComponent(ch)}')">&times;</span>
            `;
            channelsList.appendChild(pill);
        });
    } catch (error) {
        console.error(error);
    }
}

async function addChannel() {
    const name = newChannelInput.value.trim();
    if (!name) return;
    newChannelInput.value = '';
    try {
        await fetch('/api/reference-channels', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        loadChannels();
    } catch (error) {
        console.error(error);
    }
}

async function deleteChannel(name) {
    try {
        await fetch(`/api/reference-channels/${name}`, {
            method: 'DELETE'
        });
        loadChannels();
    } catch (error) {
        console.error(error);
    }
}

async function validateChatToNotion() {
    if (chatHistory.length === 0) {
        alert("La conversation est vide. Veuillez d'abord échanger avec le directeur créatif.");
        return;
    }
    
    const btn = document.getElementById('validateChatBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '⚡ Envoi en cours...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/chat/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                database_type: currentTab,
                history: chatHistory
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            btn.innerHTML = '✅ Envoyé !';
            btn.style.background = '#2ed573';
            btn.style.borderColor = '#2ed573';
            btn.style.color = '#fff';
            
            loadProjects();
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '';
                btn.style.borderColor = '';
                btn.style.color = '';
                btn.disabled = false;
            }, 3000);
        } else {
            alert(`Erreur lors de la validation : ${data.detail || 'Erreur inconnue'}`);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error(error);
        alert("Erreur réseau lors de la validation du chat.");
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

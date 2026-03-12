import json
import os
from datetime import datetime

INPUT_JSON = os.path.join('.tmp', 'top_reddit_posts.json')
OUTPUT_HTML = 'reddit_dashboard.html'

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>Reddit Automation Dashboard</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- EmailJS SDK -->
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@4/dist/email.min.js"></script>
    <script type="text/javascript">
        (function() {
            // Public Key for EmailJS setup
            emailjs.init({
              publicKey: "TlvO11tvjuzhM1Tbq", // User provided Public Key
            });
        })();
    </script>
    
    <style>
        :root {
            --bg-body: #f4f6fa;
            --grad-header: linear-gradient(135deg, #c364fa, #f55ce4);
            
            /* Card Gradients */
            --grad-1: linear-gradient(135deg, #81c7ff, #629bfb);  /* Blue */
            --grad-2: linear-gradient(135deg, #ffc977, #f49545);  /* Orange */
            --grad-3: linear-gradient(135deg, #fe7db3, #f54378);  /* Pink */
            --grad-4: linear-gradient(135deg, #ce8cfd, #9065fc);  /* Purple */
            --grad-5: linear-gradient(135deg, #60efc7, #24ce9d);  /* Mint */
            
            --text-main: #ffffff;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Nunito', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-body);
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            margin: 0;
        }

        /* Desktop Container */
        .desktop-container {
            width: 100%;
            max-width: 1440px;
            background-color: #ffffff;
            min-height: 100vh;
            position: relative;
            box-shadow: 0 0 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            margin: 0 auto;
        }

        /* Top Bar & Header */
        .app-header {
            background: var(--grad-header);
            padding: 2.5rem 3rem 0rem 3rem;
            color: white;
            border-bottom-left-radius: 20px;
            border-bottom-right-radius: 20px;
            margin-bottom: 2rem;
            position: relative;
        }

        .top-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.5rem;
            margin-bottom: 3rem;
            position: relative;
        }
        
        .header-title {
            font-weight: 800;
            font-size: 1.8rem;
            letter-spacing: -0.5px;
        }

        .icon-btn {
            cursor: pointer;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: rgba(0,0,0,0.1);
            transition: background 0.2s;
        }
        
        .icon-btn:hover {
            background: rgba(255,255,255,0.25);
        }

        /* Top Menu Dropdown */
        .top-menu {
            position: absolute;
            top: 60px;
            right: 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 8px;
            display: none;
            flex-direction: column;
            gap: 4px;
            z-index: 100;
            min-width: 240px;
        }
        .top-menu.active {
            display: flex;
            animation: menuFadeIn 0.2s ease;
        }
        @keyframes menuFadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .top-menu-item {
            padding: 12px 20px;
            color: #1e293b;
            font-size: 1.05rem;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
            transition: background 0.2s;
        }
        .top-menu-item:hover {
            background: #f1f5f9;
        }
        
        .top-menu-item i {
            color: #94a3b8;
            font-size: 1.2rem;
            width: 24px;
            text-align: center;
        }

        /* Loading Overlay */
        .loading-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.9);
            z-index: 200;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: #c364fa;
        }
        .loading-overlay.active {
            display: flex;
        }
        .loading-overlay i {
            font-size: 4rem;
            margin-bottom: 20px;
            animation: spin 1s linear infinite;
        }
        .loading-overlay p {
            font-size: 1.4rem;
            font-weight: 800;
            color: #1e293b;
        }
        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* Tabs */
        .tabs {
            display: flex;
            gap: 2.5rem;
            overflow-x: auto;
            scrollbar-width: none;
            padding-bottom: 2px;
        }
        .tabs::-webkit-scrollbar { display: none; }
        .tab {
            font-size: 1.3rem;
            font-weight: 600;
            cursor: pointer;
            position: relative;
            color: rgba(255,255,255,0.7);
            white-space: nowrap;
            padding-bottom: 16px;
            transition: color 0.2s, font-size 0.2s;
        }
        .tab.active {
            color: #ffffff;
            font-size: 1.5rem;
            font-weight: 800;
        }
        .tab.active::after {
            content: '';
            position: absolute;
            bottom: 0px; left: 0; width: 100%;
            height: 4px;
            background-color: white;
            border-radius: 4px;
        }

        /* Post Lists */
        .lists-container {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        /* Responsive Grid for Desktop */
        .post-list {
            padding: 1rem 3rem 10rem 3rem;
            display: none;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
            flex: 1;
            overflow-y: auto;
            animation: fadeIn 0.4s ease;
            align-content: start;
        }
        .post-list.active {
            display: grid;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Card Setup */
        .card {
            border-radius: 20px;
            padding: 0; /* Remove padding to handle full image */
            display: flex;
            flex-direction: column;
            color: white;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(0,0,0,0.06);
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            min-height: 180px;
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 32px rgba(0,0,0,0.12);
        }
        
        /* Apply dynamic gradients by rank */
        .card.rank-1 { background: var(--grad-1); }
        .card.rank-2 { background: var(--grad-2); }
        .card.rank-3 { background: var(--grad-3); }
        .card.rank-4 { background: var(--grad-4); }
        .card.rank-5 { background: var(--grad-5); }
        .card.rank-other { background: var(--grad-1); filter: hue-rotate(45deg); }

        /* Multi-selection styles */
        .card.selectable {
            cursor: pointer;
        }
        
        .card.selected {
            transform: scale(0.96) translateY(0);
            box-shadow: 0 0 0 4px #10b981; /* Green border */
        }
        .card.selected::before {
            content: '\\f058'; /* fa-circle-check */
            font-family: "Font Awesome 6 Free";
            font-weight: 900;
            position: absolute;
            top: 20px; left: 20px;
            font-size: 2.5rem;
            color: #10b981;
            z-index: 10;
            background: white;
            border-radius: 50%;
            height: 38px; width: 38px;
            display: flex; justify-content: center; align-items: center;
        }

        /* Optional Post Thumbnail Section */
        .post-image-wrapper {
            width: 100%;
            height: 200px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            overflow: hidden;
            flex-shrink: 0;
        }
        .post-image-wrapper img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        .card:hover .post-image-wrapper img {
            transform: scale(1.05); /* subtle zoom on hover */
        }

        /* Right Oval Shape Element inside card (keeps mobile look) */
        .card-shape {
            position: absolute;
            right: -60px;
            top: -20%;
            width: 180px;
            height: 140%;
            background: rgba(255,255,255,0.12);
            border-radius: 50%;
            z-index: 1;
            pointer-events: none;
        }

        /* Card Content Layer */
        .card-content {
            position: relative;
            z-index: 2;
            display: flex;
            width: 100%;
            padding: 1.5rem;
            flex: 1; /* take remaining height */
        }

        .avatar-col {
            margin-right: 20px;
            flex-shrink: 0;
        }
        .avatar-col img {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            object-fit: cover;
            background: rgba(255,255,255,0.2);
            border: 3px solid rgba(255,255,255,0.5);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .info-col {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-right: 12px;
            min-width: 0; /* fixes truncate bug in flex */
        }
        .author-name {
            font-size: 1.25rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .post-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: rgba(255,255,255,0.95);
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.4;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .stats-row {
            display: flex;
            gap: 20px;
            font-size: 0.85rem;
            font-weight: 800;
            text-align: center;
        }
        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }
        .stat-value {
            font-size: 1.1rem;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .stat-label {
            color: rgba(255,255,255,0.85);
            font-size: 0.75rem;
            font-weight: 700;
        }

        .rank-col {
            width: 70px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding-top: 2px;
            position: relative;
            flex-shrink: 0;
            border-left: 1px solid rgba(255,255,255,0.2);
            margin-left: 8px;
        }
        .rank-dots {
            font-size: 1.8rem;
            line-height: 0.3;
            letter-spacing: 2px;
            margin-bottom: auto;
            color: rgba(255,255,255,0.9);
        }
        .rank-number {
            font-size: 2.2rem;
            font-weight: 900;
            margin-top: 14px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }
        .rank-label {
            font-size: 0.8rem;
            font-weight: 700;
            color: rgba(255,255,255,0.9);
            margin-bottom: 4px;
        }

        /* Selection Bottom Action Bar */
        .selection-bar {
            position: absolute;
            bottom: -150px; left: 0; right: 0;
            background: #ffffff;
            padding: 1.5rem 3rem;
            box-shadow: 0 -10px 40px rgba(0,0,0,0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            transition: bottom 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 50;
        }
        .selection-bar.active {
            bottom: 0;
        }
        .selection-count {
            font-weight: 800;
            color: #1e293b;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .selection-count span {
            background:#f1f5f9; 
            padding:6px 16px; 
            border-radius:12px; 
            color:#c364fa;
            font-size: 1.3rem;
        }
        
        .selection-actions {
            display: flex;
            gap: 16px;
        }
        .btn-cancel {
            background: #f1f5f9;
            color: #64748b;
            border: none;
            padding: 14px 24px;
            border-radius: 12px;
            font-weight: 800;
            cursor: pointer;
            font-size: 1.05rem;
            transition: background 0.2s;
        }
        .btn-cancel:hover { background: #e2e8f0; }
        
        .btn-send {
            background: var(--grad-header);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 12px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 6px 15px rgba(189, 98, 255, 0.35);
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 1.05rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn-send:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(189, 98, 255, 0.45);
        }

        /* Toast Notification */
        .toast-container {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 500;
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: none;
        }
        .toast {
            background: white;
            color: #1e293b;
            padding: 16px 20px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            font-weight: 700;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 12px;
            transform: translateX(120%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 5px solid #3b82f6;
            max-width: 320px;
        }
        .toast.success { border-left-color: #10b981; }
        .toast.error { border-left-color: #ef4444; }
        .toast.info { border-left-color: #c364fa; }
        .toast.show { transform: translateX(0); }

        /* Email Config Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(4px);
            z-index: 300;
            display: none;
            justify-content: center;
            align-items: center;
            animation: fadeIn 0.2s;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal-card {
            background: white;
            width: 90%;
            max-width: 400px;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            position: relative;
        }
        .modal-title {
            font-size: 1.25rem;
            font-weight: 800;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        .modal-desc {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        .email-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            color: #1e293b;
            outline: none;
            transition: border-color 0.2s;
            margin-bottom: 1.5rem;
        }
        .email-input:focus {
            border-color: #c364fa;
        }
        .modal-btn {
            width: 100%;
            background: var(--grad-header);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.05rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .modal-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(189, 98, 255, 0.35);
        }
        .close-modal {
            position: absolute;
            top: 16px; right: 20px;
            font-size: 1.5rem;
            color: #cbd5e1;
            cursor: pointer;
            transition: color 0.2s;
        }
        .close-modal:hover { color: #64748b; }

    </style>
</head>
<body>

    <div class="desktop-container">
        
        <!-- Loading Overlay -->
        <div class="loading-overlay" id="loadingOverlay">
            <i class="fa-solid fa-spinner"></i>
            <p>Atualizando Dados...</p>
        </div>

        <!-- Top App Bar Base -->
        <div class="app-header">
            <div class="top-row">
                <div class="header-title"><i class="fa-solid fa-bolt" style="margin-right:12px;"></i> AutomateHub</div>
                
                <!-- Main interaction Menu Icon -->
                <div class="icon-btn" onclick="toggleMenu(event)"><i class="fa-solid fa-bars" style="font-size: 1.8rem;"></i></div>
                
                <div class="top-menu" id="topMenu">
                    <div class="top-menu-item" onclick="refreshData()">
                        <i class="fa-solid fa-rotate-right"></i> Atualizar Dados
                    </div>
                    <div class="top-menu-item" onclick="openEmailConfig()">
                        <i class="fa-solid fa-gear"></i> Configurar E-mail
                    </div>
                    <div class="top-menu-item" onclick="activateSelectionMode()">
                        <i class="fa-regular fa-paper-plane"></i> Selecionar para Envio
                    </div>
                </div>
            </div>

            <div class="tabs" id="navTabs">
                <!-- Injected by JS -->
            </div>
        </div>

        <!-- Scrollable Post Lists -->
        <div class="lists-container" id="listsContainer">
            <!-- Lists injected by JS -->
        </div>

        <!-- Selection Mode Bottom Action Area -->
        <div class="selection-bar" id="selectionBar">
            <div class="selection-count">
                Selecionados: <span id="selCount">0</span>
            </div>
            <div class="selection-actions">
                <button class="btn-cancel" onclick="cancelSelection()">Cancelar</button>
                <button class="btn-send" onclick="sendSelectedEmail()">
                    <i class="fa-solid fa-envelope"></i> Enviar (<span id="btnSendCount">0</span>)
                </button>
            </div>
        </div>

        <!-- Floating Email Config Modal -->
        <div class="modal-overlay" id="emailModal" onclick="closeEmailConfig(event)">
            <div class="modal-card" onclick="event.stopPropagation()">
                <i class="fa-solid fa-xmark close-modal" onclick="closeEmailConfig()"></i>
                <h3 class="modal-title">Configurar Destino</h3>
                <p class="modal-desc">Para qual endereço de e-mail você deseja enviar os posts selecionados?</p>
                
                <input type="email" id="targetEmailInput" class="email-input" placeholder="exemplo@gmail.com">
                
                <button class="modal-btn" onclick="saveEmailConfig()">Salvar E-mail</button>
            </div>
        </div>

        <!-- Toast Notifications Container -->
        <div class="toast-container" id="toastContainer"></div>

    </div>

    <script>
        const redditData = REDDIT_DATA_INJECTED_HERE;

        // Custom config to match requested design Tabs
        const TOPICS_CONFIG = {
            'n8n': { label: 'Comunidade n8n' },
            'automation': { label: 'Automation' }
        };

        const navTabs = document.getElementById('navTabs');
        const listsContainer = document.getElementById('listsContainer');
        const topMenu = document.getElementById('topMenu');
        
        let subreddits = Object.keys(redditData);
        let activeSub = null;

        // Selection mode state variables
        let isSelectionMode = false;
        let selectedPosts = new Set(); 

        function initApp() {
            if (subreddits.length === 0) return;

            subreddits.forEach((sub, index) => {
                const config = TOPICS_CONFIG[sub] || { label: sub.toUpperCase() };
                
                // 1. Create Tab Element
                const tabBtn = document.createElement('div');
                tabBtn.className = `tab ${index === 0 ? 'active' : ''}`;
                tabBtn.textContent = config.label;
                tabBtn.onclick = () => switchTab(sub, tabBtn);
                navTabs.appendChild(tabBtn);

                // 2. Create actual List Container for posts under this tab
                const listEl = document.createElement('div');
                listEl.id = `list-${sub}`;
                listEl.className = `post-list ${index === 0 ? 'active' : ''}`;
                
                const posts = redditData[sub];

                if (!posts || posts.length === 0) {
                    listEl.innerHTML = `<div style="text-align:center; padding-top: 40px; color: #94a3b8; font-size:1.2rem; font-weight:700; grid-column: 1/-1;">Nenhum conteúdo encontrado.</div>`;
                } else {
                    posts.forEach((post, i) => {
                        const title = (post.title || 'Post sem título').replace(/\\n/g, ' ');
                        const score = post.score || 0;
                        const comments = post.num_comments || 0;
                        const permalink = `https://www.reddit.com${post.permalink || ''}`;
                        const author = post.author || 'anon';
                        
                        // Extract Avatar
                        let avatarUrl = post.author_icon_url;
                        if (!avatarUrl) {
                            avatarUrl = `https://i.pravatar.cc/150?u=${encodeURIComponent(author)}&size=150`;
                        }
                        const fallbackImg = `https://i.pravatar.cc/150?u=${encodeURIComponent(author)}&size=150`;
                        const imgError = `this.onerror=null;this.src='${fallbackImg}';`;

                        // Select Rank logic
                        const rankNum = i + 1;
                        const rankClass = rankNum <= 5 ? `rank-${rankNum}` : `rank-other`;

                        // Prevent string breaks in HTML
                        const safeTitle = title.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                        
                        // Faux "Followed" stat for design parity
                        const followedStat = Math.floor(Math.random() * 200) + 50;

                        // Check if Post Has Image to display above text
                        let postImageHtml = '';
                        let postImageUrl = null;
                        
                        if (post.thumbnail && post.thumbnail.startsWith('http')) {
                            postImageUrl = post.thumbnail;
                        } else if (post.url && (post.url.endsWith('.jpg') || post.url.endsWith('.png') || post.url.endsWith('.gif'))) {
                            postImageUrl = post.url;
                        } else if (post.preview && post.preview.images && post.preview.images.length > 0) {
                            postImageUrl = post.preview.images[0].source.url.replace(/&amp;/g, '&');
                        }

                        if (postImageUrl) {
                            postImageHtml = `
                                <div class="post-image-wrapper">
                                    <img src="${postImageUrl}" alt="Post Image">
                                </div>
                            `;
                        }

                        listEl.innerHTML += `
                            <a href="${permalink}" target="_blank" data-url="${permalink}" data-title="${safeTitle}" data-author="${author}" 
                               class="card ${rankClass}" 
                               onclick="handleCardInteraction(event, this)">
                                
                                <div class="card-shape"></div>
                                
                                ${postImageHtml}
                                
                                <div class="card-content">
                                    <div class="avatar-col">
                                        <img src="${avatarUrl}" onerror="${imgError}" alt="Author Avatar">
                                    </div>
                                    
                                    <div class="info-col">
                                        <div class="author-name">${author}</div>
                                        <div class="post-title" title="${safeTitle}">Título: ${title}</div>
                                        
                                        <div class="stats-row">
                                            <div class="stat-item">
                                                <span class="stat-value">${score}</span>
                                                <span class="stat-label">Popularity</span>
                                            </div>
                                            <div class="stat-item">
                                                <span class="stat-value">${comments}</span>
                                                <span class="stat-label">Like</span>
                                            </div>
                                            <div class="stat-item">
                                                <span class="stat-value">${followedStat}</span>
                                                <span class="stat-label">Followed</span>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="rank-col" title="Top Post Ranking">
                                        <div class="rank-dots">...</div>
                                        <div class="rank-number">${rankNum}</div>
                                        <div class="rank-label">Ranking</div>
                                    </div>
                                </div>
                            </a>
                        `;
                    });
                }
                
                listsContainer.appendChild(listEl);
            });

            activeSub = subreddits[0];
        }

        function switchTab(sub, btnElement) {
            if (activeSub === sub) return;

            document.querySelectorAll('.tab').forEach(btn => btn.classList.remove('active'));
            btnElement.classList.add('active');

            document.querySelectorAll('.post-list').forEach(list => list.classList.remove('active'));
            document.getElementById(`list-${sub}`).classList.add('active');

            activeSub = sub;
            cancelSelection(); // Always cancel mode on tab switch
        }

        // ---------- Top Menu Logic ----------
        function toggleMenu(e) {
            e.stopPropagation();
            topMenu.classList.toggle('active');
        }
        document.addEventListener('click', () => {
             topMenu.classList.remove('active');
        });
        topMenu.addEventListener('click', (e) => e.stopPropagation());

        // ---------- Fetch Backend / Refresh Data ----------
        async function refreshData() {
            topMenu.classList.remove('active');
            const overlay = document.getElementById('loadingOverlay');
            overlay.classList.add('active');

            try {
                const response = await fetch('/api/refresh', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (!response.ok) throw new Error("Erro no servidor");
                const result = await response.json();
                
                if (result.status === 'success') {
                    window.location.reload();
                } else {
                    throw new Error(result.message);
                }
            } catch (err) {
                console.error("Refresh fallhou:", err);
                alert("Não foi possível conectar com o python (server.py). Verifique se ele está rodando.");
                overlay.classList.remove('active');
            }
        }

        // ---------- Multi-Select Email Logic ----------
        function activateSelectionMode() {
            topMenu.classList.remove('active');
            isSelectionMode = true;
            selectedPosts.clear();
            
            document.getElementById('selectionBar').classList.add('active');
            
            document.querySelectorAll('.card').forEach(c => {
                c.classList.add('selectable');
                c.classList.remove('selected');
                c.removeAttribute('target');    // Remove generic target when selectable
            });
            updateSelCount();
        }

        function cancelSelection() {
            isSelectionMode = false;
            document.getElementById('selectionBar').classList.remove('active');
            
            document.querySelectorAll('.card').forEach(c => {
                c.classList.remove('selectable', 'selected');
                c.setAttribute('target', '_blank'); // Give back target normal mode
            });
        }

        function handleCardInteraction(event, cardEl) {
            if (!isSelectionMode) {
                // If not in mode, let default `href` click navigate to reddit normally
                return;
            }
            
            // Prevention of default navigation when Select Mode active
            event.preventDefault();
            
            const url = cardEl.getAttribute('data-url');
            
            if (selectedPosts.has(url)) {
                selectedPosts.delete(url);
                cardEl.classList.remove('selected');
            } else {
                selectedPosts.add(url);
                cardEl.classList.add('selected');
            }
            updateSelCount();
        }

        function updateSelCount() {
            const count = selectedPosts.size;
            document.getElementById('selCount').innerText = count;
            document.getElementById('btnSendCount').innerText = count;
        }

        // ---------- Toast Notifications ----------
        function showToast(message, type="info", persistent=false) {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            
            let icon = 'fa-circle-info';
            if(type === 'success') icon = 'fa-circle-check';
            if(type === 'error') icon = 'fa-circle-xmark';
            if(type === 'info' && persistent) icon = 'fa-spinner fa-spin';

            toast.innerHTML = `<i class="fa-solid ${icon}" style="font-size: 1.4rem;"></i> <span>${message}</span>`;
            
            container.appendChild(toast);
            
            // Trigger animation
            setTimeout(() => toast.classList.add('show'), 10);

            if(!persistent) {
                setTimeout(() => {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 300);
                }, 4000);
            }
            return toast; // return element to allow manual removal
        }

        // ---------- Config Modal Logic ----------
        function openEmailConfig() {
            topMenu.classList.remove('active');
            const savedEmail = localStorage.getItem('ope_target_email') || '';
            document.getElementById('targetEmailInput').value = savedEmail;
            document.getElementById('emailModal').classList.add('active');
        }

        function closeEmailConfig(e) {
            // Se e existe e foi clicado no overlay bg
            if(e && e.target !== document.getElementById('emailModal')) return; 
            document.getElementById('emailModal').classList.remove('active');
        }

        function saveEmailConfig() {
            const val = document.getElementById('targetEmailInput').value.trim();
            if(val) {
                localStorage.setItem('ope_target_email', val);
                document.getElementById('emailModal').classList.remove('active');
                showToast("E-mail " + val + " salvo com sucesso!", "success");
            } else {
                showToast("Por favor insira um e-mail válido.", "error");
            }
        }

        async function sendSelectedEmail() {
            if (selectedPosts.size === 0) {
                showToast("Por favor selecione pelo menos um post para enviar o email!", "error");
                return;
            }
            
            const targetEmail = localStorage.getItem('ope_target_email') || '';
            if(!targetEmail) {
                showToast("Você precisa configurar seu e-mail de destino primeiro!", "error");
                openEmailConfig();
                return;
            }

            // Construindo o e-mail em formato HTML profissional (Estilo Credit Pros)
            let htmlBody = `
            <div style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background-color: #fffaf5; padding: 40px 20px; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                    
                    <!-- Header Secao -->
                    <div style="background: linear-gradient(135deg, #f97316, #fb923c); padding: 35px 20px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0.5px;">💡 Destaques AutomateHub</h1>
                        <p style="color: #fff7ed; margin-top: 8px; font-size: 15px;">Os melhores insights de automação que você pescou no Reddit.</p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 30px 20px;">
                        <h2 style="text-align: center; color: #1e293b; font-size: 20px; margin-bottom: 25px;">Seus posts favoritos:</h2>
            `;
            
            document.querySelectorAll('.card.selected').forEach(card => {
                const title = card.getAttribute('data-title');
                const author = card.getAttribute('data-author');
                const url = card.getAttribute('data-url');
                const imgEl = card.querySelector('.post-image');
                const avatarEl = card.querySelector('.avatar');
                
                let imageUrl = '';
                if (imgEl && imgEl.hasAttribute('src')) {
                    imageUrl = imgEl.src;
                } else if (avatarEl && avatarEl.hasAttribute('src')) {
                    imageUrl = avatarEl.src;
                }

                htmlBody += `
                        <!-- Post Card (Estetica Credit Pros com Sombras e Botoes Laranjas) -->
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 25px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
                            ${imageUrl ? '<img src="' + imageUrl + '" style="width: 100%; height: 220px; object-fit: cover; border-bottom: 1px solid #e2e8f0;" alt="Imagem do Post">' : ''}
                            <div style="padding: 24px;">
                                <div style="font-size: 12px; font-weight: bold; color: #f97316; text-transform: uppercase; margin-bottom: 8px;">POR: ${author}</div>
                                <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #0f172a; line-height: 1.4;">${title}</h3>
                                <div style="text-align: left;">
                                    <a href="${url}" style="display: inline-block; background-color: #f97316; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 25px; font-weight: bold; font-size: 14px; text-align: center; box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3);">Ler Post Completo &rarr;</a>
                                </div>
                            </div>
                        </div>
                `;
            });
            
            htmlBody += `
                    </div>
                    
                    <!-- Footer Info -->
                    <div style="background-color: #f1f5f9; padding: 24px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b;">
                        <p style="margin: 0; font-weight: bold;">AutomateHub Dashboard &copy; 2026</p>
                        <p style="margin: 5px 0 0 0;">Automação de Captura e Envio de E-mails via n8n e Python</p>
                    </div>
                </div>
            </div>
            `;
            
            const subject = "Posts e Insights que selecionei direto do Reddit";
            
            const loadingToast = showToast("Enviando e-mail, por favor aguarde...", "info", true);

            try {
                // Using EmailJS for backend-less SMTP delivery avoiding App Passwords
                const templateParams = {
                    to_email: targetEmail,
                    from_name: "AutomateHub",
                    subject: subject,
                    message: htmlBody
                };

                // Using User's Service ID and custom template
                const response = await emailjs.send('service_hww88v9', 'template_l0olb4n', templateParams);

                loadingToast.classList.remove('show');
                setTimeout(() => loadingToast.remove(), 300);

                if (response.status === 200) {
                    showToast("E-mail enviado com sucesso!", "success");
                    cancelSelection();
                } else {
                    throw new Error("Resposta estranha da API");
                }
            } catch (err) {
                console.error("EmailJS failed:", err);
                loadingToast.classList.remove('show');
                setTimeout(() => loadingToast.remove(), 300);
                showToast("Erro ao enviar! O serviço de e-mail limitou o teste. Crie uma key no site deles.", "error");
            }
        }

        // Boot Main
        initApp();
    </script>
</body>
</html>
"""

def generate_dashboard():
    print(f"Reading data from {INPUT_JSON}...")
    
    data = {}
    if os.path.exists(INPUT_JSON):
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print(f"WARNING: Data file {INPUT_JSON} not found. Run scrape_reddit.py first.")

    # Inject JSON map into the HTML template
    html_content = HTML_TEMPLATE.replace(
        'REDDIT_DATA_INJECTED_HERE',
        json.dumps(data)
    )

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\nSuccess! UI rebuilt to Full Width Desktop layout. Dashboard generated at: {os.path.abspath(OUTPUT_HTML)}")

if __name__ == "__main__":
    generate_dashboard()

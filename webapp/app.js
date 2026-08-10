// Инициализация Telegram WebApp
const tg = window.Telegram?.WebApp;
if (tg) {
    tg.ready();
    tg.expand();
    try {
        tg.setHeaderColor('#0a0d14');
        tg.setBackgroundColor('#0a0d14');
    } catch (e) {}
}

const tgUser = tg?.initDataUnsafe?.user || {
    id: 12345678,
    first_name: "Nazar",
    username: "Ghoul23062"
};

let allMembers = [];
let currentMemberData = null;

// ================== НАВИГАЦИЯ ПО ВКЛАДКАМ ==================
const navButtons = document.querySelectorAll('.nav-btn');
const tabContents = document.querySelectorAll('.tab-content');

navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTabId = btn.getAttribute('data-tab');
        
        // Haptic feedback
        if (tg?.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('light');
        }

        navButtons.forEach(b => b.classList.remove('active'));
        tabContents.forEach(t => t.classList.remove('active'));

        btn.classList.add('active');
        const targetTab = document.getElementById(targetTabId);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    });
});

// ================== ЗАГРУЗКА ДАННЫХ ПРОФИЛЯ ==================
async function loadUserProfile() {
    const userId = tgUser.id;
    try {
        const res = await fetch(`/api/member?user_id=${userId}`);
        if (res.ok) {
            const data = await res.json();
            if (data.found) {
                currentMemberData = data.member;
                renderProfile(currentMemberData);
                return;
            }
        }
    } catch (e) {
        console.error("Ошибка загрузки профиля:", e);
    }

    // Дефолтный вид профиля, если пользователя еще нет в базе
    renderDefaultProfile();
}

function renderProfile(member) {
    document.getElementById('headerGreeting').textContent = "Добро пожаловать";
    document.getElementById('headerName').textContent = member.name || member.full_name;
    document.getElementById('headerRoleBadge').textContent = member.role || "Участник";

    document.getElementById('profileSkinImg').src = member.avatar_url || "https://tr.rbxcdn.com/30DAY-Avatar-720x720.png";
    document.getElementById('profileName').textContent = member.name;
    document.getElementById('profileRobloxNick').textContent = `@${member.roblox_username} (${member.roblox_display_name || member.roblox_username})`;
    
    const roleTag = document.getElementById('profileRoleTag');
    roleTag.textContent = member.role;
    roleTag.className = `role-tag ${getRoleClass(member.role)}`;

    document.getElementById('profileAge').textContent = `${member.age} лет`;
    document.getElementById('profileCountry').textContent = member.country;
    document.getElementById('profileRobloxId').textContent = member.roblox_id || "—";
    document.getElementById('profileRobloxDate').textContent = member.roblox_created || "—";

    const robloxLink = document.getElementById('profileRobloxLink');
    robloxLink.href = `https://www.roblox.com/users/${member.roblox_id}/profile`;
}

function renderDefaultProfile() {
    const displayName = tgUser.first_name || "Гость";
    document.getElementById('headerGreeting').textContent = "Roblox House";
    document.getElementById('headerName').textContent = displayName;
    document.getElementById('headerRoleBadge').textContent = "Новичок";

    document.getElementById('profileName').textContent = displayName;
    document.getElementById('profileRobloxNick').textContent = tgUser.username ? `@${tgUser.username}` : "Не привязан";
    document.getElementById('profileAge').textContent = "—";
    document.getElementById('profileCountry').textContent = "—";
    document.getElementById('profileRobloxId').textContent = "—";
    document.getElementById('profileRobloxDate').textContent = "—";
}

function getRoleClass(role) {
    if (role === "Создатель") return "role-creator";
    if (role === "Администратор") return "role-admin";
    return "role-member";
}

// ================== ЗАГРУЗКА И ПОИСК УЧАСТНИКОВ ==================
async function loadMembers() {
    const grid = document.getElementById('membersGrid');
    try {
        const res = await fetch('/api/members');
        if (res.ok) {
            allMembers = await res.json();
            renderMembers(allMembers);
            document.getElementById('membersCountBadge').textContent = `Всего: ${allMembers.length}`;
            return;
        }
    } catch (e) {
        console.error("Ошибка загрузки списка участников:", e);
    }

    grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color: var(--text-muted); padding: 40px 0;">Пока нет участников в базе</div>`;
}

function renderMembers(members) {
    const grid = document.getElementById('membersGrid');
    if (!members || members.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color: var(--text-muted); padding: 40px 0;">Участники не найдены</div>`;
        return;
    }

    grid.innerHTML = members.map(m => `
        <div class="member-card glass-panel" onclick="openMemberModal(${m.user_id})">
            <img class="member-avatar" src="${m.avatar_url || 'https://tr.rbxcdn.com/30DAY-Avatar-720x720.png'}" alt="${m.name}">
            <h4 class="member-name">${escapeHtml(m.name || m.full_name)}</h4>
            <p class="member-roblox">@${escapeHtml(m.roblox_username || '')}</p>
            <span class="role-tag ${getRoleClass(m.role)}">${m.role || 'Участник'}</span>
        </div>
    `).join('');
}

// Поиск
const searchInput = document.getElementById('memberSearchInput');
searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        renderMembers(allMembers);
        return;
    }

    const filtered = allMembers.filter(m => 
        (m.name && m.name.toLowerCase().includes(query)) ||
        (m.roblox_username && m.roblox_username.toLowerCase().includes(query)) ||
        (m.country && m.country.toLowerCase().includes(query))
    );
    renderMembers(filtered);
});

// ================== МОДАЛЬНОЕ ОКНО УЧАСТНИКА ==================
function openMemberModal(userId) {
    const member = allMembers.find(m => m.user_id === userId);
    if (!member) return;

    if (tg?.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('medium');
    }

    document.getElementById('modalAvatar').src = member.avatar_url || "https://tr.rbxcdn.com/30DAY-Avatar-720x720.png";
    document.getElementById('modalName').textContent = member.name || member.full_name;
    document.getElementById('modalRoblox').textContent = `@${member.roblox_username} (${member.roblox_display_name || ''})`;
    
    const roleEl = document.getElementById('modalRole');
    roleEl.textContent = member.role || "Участник";
    roleEl.className = `role-tag ${getRoleClass(member.role)}`;

    document.getElementById('modalAge').textContent = `${member.age || '—'} лет`;
    document.getElementById('modalCountry').textContent = member.country || '—';
    document.getElementById('modalJoined').textContent = member.joined_at || '—';

    const tgLink = document.getElementById('modalTgLink');
    if (member.username) {
        tgLink.href = `https://t.me/${member.username}`;
        tgLink.style.display = "flex";
    } else {
        tgLink.style.display = "none";
    }

    document.getElementById('modalRobloxLink').href = `https://www.roblox.com/users/${member.roblox_id}/profile`;

    document.getElementById('memberModal').classList.remove('hidden');
}

document.getElementById('closeModalBtn').addEventListener('click', () => {
    document.getElementById('memberModal').classList.add('hidden');
});

document.getElementById('memberModal').addEventListener('click', (e) => {
    if (e.target.id === 'memberModal') {
        document.getElementById('memberModal').classList.add('hidden');
    }
});

// ================== КОЛЕСО УДАЧИ ==================
const canvas = document.getElementById('wheelCanvas');
const ctx = canvas.getContext('2d');
const spinBtn = document.getElementById('spinBtn');
const bonusResult = document.getElementById('bonusResult');
const bonusPrizeText = document.getElementById('bonusPrizeText');

const prizes = [
    { label: "⭐ 100 XP", color: "#ff2d55" },
    { label: "👑 Титул VIP", color: "#8b5cf6" },
    { label: "🍀 Удача +50%", color: "#00f0ff" },
    { label: "💖 Респект", color: "#ec4899" },
    { label: "🗡️ Слот в MM2", color: "#f59e0b" },
    { label: "💃 Топ Танцор", color: "#10b981" },
    { label: "🔥 Огонь", color: "#ef4444" },
    { label: "🎁 Сюрприз", color: "#6366f1" }
];

let startAngle = 0;
const arc = Math.PI / (prizes.length / 2);
let spinTimeout = null;
let spinArcStart = 10;
let spinTime = 0;
let spinTimeTotal = 0;
let isSpinning = false;

function drawWheel() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const outsideRadius = 135;
    const textRadius = 95;
    const insideRadius = 30;

    for (let i = 0; i < prizes.length; i++) {
        const angle = startAngle + i * arc;
        ctx.fillStyle = prizes[i].color;

        ctx.beginPath();
        ctx.arc(150, 150, outsideRadius, angle, angle + arc, false);
        ctx.arc(150, 150, insideRadius, angle + arc, angle, true);
        ctx.fill();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.save();
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 12px Outfit, sans-serif";
        ctx.translate(150 + Math.cos(angle + arc / 2) * textRadius, 
                      150 + Math.sin(angle + arc / 2) * textRadius);
        ctx.rotate(angle + arc / 2 + Math.PI / 2);
        const text = prizes[i].label;
        ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
        ctx.restore();
    }

    // Центр колеса
    ctx.beginPath();
    ctx.arc(150, 150, insideRadius, 0, Math.PI * 2, false);
    ctx.fillStyle = "#0a0d14";
    ctx.fill();
    ctx.strokeStyle = "#ff2d55";
    ctx.lineWidth = 3;
    ctx.stroke();
}

function rotateWheel() {
    spinTime += 30;
    if (spinTime >= spinTimeTotal) {
        stopRotateWheel();
        return;
    }
    const spinAngle = spinArcStart - easeOut(spinTime, 0, spinArcStart, spinTimeTotal);
    startAngle += (spinAngle * Math.PI / 180);
    drawWheel();
    spinTimeout = setTimeout(rotateWheel, 30);
}

function stopRotateWheel() {
    clearTimeout(spinTimeout);
    isSpinning = false;
    spinBtn.disabled = false;
    const degrees = startAngle * 180 / Math.PI + 90;
    const arcd = arc * 180 / Math.PI;
    const index = Math.floor((360 - degrees % 360) / arcd) % prizes.length;
    const prize = prizes[index];

    bonusPrizeText.textContent = `Твой выигрыш: ${prize.label}! 🎉`;
    bonusResult.classList.remove('hidden');

    if (tg?.HapticFeedback) {
        tg.HapticFeedback.notificationOccurred('success');
    }
}

function easeOut(t, b, c, d) {
    const ts = (t /= d) * t;
    const tc = ts * t;
    return b + c * (tc + -3 * ts + 3 * t);
}

spinBtn.addEventListener('click', () => {
    if (isSpinning) return;
    isSpinning = true;
    spinBtn.disabled = true;
    bonusResult.classList.add('hidden');

    if (tg?.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('heavy');
    }

    spinArcStart = Math.random() * 10 + 10;
    spinTime = 0;
    spinTimeTotal = Math.random() * 2000 + 3000;
    rotateWheel();
});

function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// Запуск при старте
window.addEventListener('DOMContentLoaded', () => {
    drawWheel();
    loadUserProfile();
    loadMembers();
});

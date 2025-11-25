document.addEventListener('DOMContentLoaded', () => {
    const games = [
        {
            id: 1,
            title: '节奏光环',
            genre: '街机 / 电子',
            platform: 'pc',
            imageUrl: 'https://images.unsplash.com/photo-1587213699923-1f10asona123?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '在这款充满活力的街机风格节奏游戏中，跟随脉动的电子节拍，穿过霓虹灯闪烁的隧道。精准度和反应速度是关键。'
        },
        {
            id: 2,
            title: '星际节拍',
            genre: '科幻 / 流行',
            platform: 'mobile',
            imageUrl: 'https://images.unsplash.com/photo-1534796636912-3b95b3eab598?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '在星际间航行，根据宇宙流行音乐的节拍点击行星。探索新的星系，解锁具有独特音轨的飞船。'
        },
        {
            id: 3,
            title: '霓虹深渊',
            genre: '赛博朋克 / 摇滚',
            platform: 'pc',
            imageUrl: 'https://images.unsplash.com/photo-1555617340-057416f64d0a?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '潜入一个反乌托邦的赛博朋克世界。在这款基于故事的节奏游戏中，与叛逆的摇滚配乐同步，对抗腐败的公司。'
        },
        {
            id: 4,
            title: '古典回响',
            genre: '钢琴 / 古典',
            platform: 'mobile',
            imageUrl: 'https://images.unsplash.com/photo-1518600573729-6a344934142d?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '通过这款优雅的钢琴节奏游戏，体验莫扎特、贝多芬和肖邦的永恒杰作。非常适合古典音乐爱好者。'
        },
        {
            id: 5,
            title: '都市律动',
            genre: '嘻哈 / R&B',
            platform: 'mobile',
            imageUrl: 'https://images.unsplash.com/photo-1506157786151-b8491531f063?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '在充满活力的都市景观中，感受嘻哈和R&B的流畅节拍。自定义你的角色，在街头风格的节奏对战中一决高下。'
        },
        {
            id: 6,
            title: '幻境音符',
            genre: '动漫 / J-Pop',
            platform: 'pc',
            imageUrl: 'https://images.unsplash.com/photo-1614850523259-0a9a46399839?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '进入一个神奇的动漫世界，随着迷人的J-Pop曲调点击。收集可爱的角色，揭开一个充满音乐魔法的迷人故事。'
        },
        {
            id: 7,
            title: '沙漠鼓点',
            genre: '世界音乐 / 打击乐',
            platform: 'pc',
            imageUrl: 'https://images.unsplash.com/photo-1516422348325-1311548c71b6?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '踏上一场穿越广阔沙漠的节奏之旅。根据充满异国情调的世界音乐和复杂的鼓点节奏敲击。'
        },
        {
            id: 8,
            title: '爵士之夜',
            genre: '爵士 / 摇摆乐',
            platform: 'mobile',
            imageUrl: 'https://images.unsplash.com/photo-1509714312-e5b9f4b8a2e5?q=80&w=800&h=1000&auto=format&fit=crop',
            description: '在一家舒适的地下酒吧里，让自己沉浸在爵士乐和摇摆乐的即兴节奏中。感受音乐，让节拍引导你的每一次点击。'
        }
    ];

    const gameGrid = document.getElementById('game-grid');
    const modal = document.getElementById('myModal');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const closeModal = document.querySelector('.close');
    const filterButtons = document.querySelectorAll('.filter-btn');

    function renderGames(filter = 'all') {
        gameGrid.innerHTML = '';
        const filteredGames = games.filter(game => filter === 'all' || game.platform === filter);

        filteredGames.forEach(game => {
            const gameCard = document.createElement('div');
            gameCard.className = 'game-card';
            gameCard.innerHTML = `
                <div class="card-image-wrapper">
                    <img src="${game.imageUrl}" alt="${game.title}" class="game-card-image">
                </div>
                <div class="game-card-content">
                    <h3 class="game-card-title">${game.title}</h3>
                    <p class="game-card-genre">${game.genre}</p>
                    <a href="#" class="download-button">查看详情</a>
                </div>
            `;
            
            gameCard.addEventListener('click', (e) => {
                e.preventDefault();
                modalTitle.textContent = game.title;
                modalDescription.textContent = game.description;
                modal.style.display = 'block';
            });

            gameGrid.appendChild(gameCard);
        });
    }

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const filter = button.dataset.filter;
            renderGames(filter);
        });
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    renderGames();
});

document.addEventListener('DOMContentLoaded', () => {
    const games = [
        {            id: 1,
            title: 'OSU!',
            genre: '音乐/PC',
            platform: 'pc',
            imageUrl: 'https://pan.gu-chen.top/f/nqFp/lazer.png',
            description: 'PC端经典音游，内含Std,mania,taiko等模式',
            downloads: [{ name: 'Github Release', url: 'https://github.com/ppy/osu/releases' }, { name: '官网下载', url: 'https://osu.ppy.sh/home/download' }, { name: '网盘下载', url: 'https://pan.gu-chen.top/f/qOco/osu.zip' }],
        },
        {            id: 2,
            title: 'Malody(PC端)',
            genre: 'PC/社区/音乐',
            platform: 'pc',
            imageUrl: 'https://pan.gu-chen.top/f/Rnfv/Malody4.0.png',
            description: '一款跨平台的多种游玩方式的音乐游戏\n支持Maina、Catch等模式',
            downloads: [{ name: '官方Steam(V版)', url: 'https://store.steampowered.com/app/1512940/Malody_V/' }, { name: 'Windows(4.3.7)', url: 'https://pan.gu-chen.top/f/a4U6/Malody-4.3.7.7z' }, { name: 'Mac(3.4.7)', url: 'https://pan.gu-chen.top/f/EeiV/Malody-3.4.7%28MAC%29.zip' }],
        },
        {            id: 3,
            title: 'DJMAX RESPECT V',
            genre: 'PC/多Key/正版',
            platform: 'pc',
            imageUrl: 'https://ts1.tc.mm.bing.net/th/id/R-C.344db693c306dc3c177d0381e887412d?rik=pGE9fgRCDTP2Mg&riu=http%3a%2f%2fbirb.uk%2fimages%2fdjmax.jpg&ehk=xGgzUoSszjuLOj52B0GNptqhWLvXZMA3okEZdZyyps0%3d&risl=&pid=ImgRaw&r=0',
            description: '最佳人气音游《DJMAX》终于上线STEAM了！ DJMAX系列的最新作品《DJMAX RESPECT》以进一步发展的内容推出在Steam。',
            downloads: [{ name: 'Steam', url: 'https://store.steampowered.com/app/960170/DJMAX_RESPECT_V/' }],
        },
    ];

    const gameGrid = document.getElementById('game-grid');
    const modal = document.getElementById('myModal');
    const modalTitle = document.getElementById('modal-title');
    const modalDescription = document.getElementById('modal-description');
    const modalDownloads = document.getElementById('modal-downloads');
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

                modalDownloads.innerHTML = '';
                if (game.downloads && game.downloads.length > 0) {
                    game.downloads.forEach(download => {
                        const downloadLink = document.createElement('a');
                        downloadLink.href = download.url;
                        downloadLink.textContent = download.name;
                        downloadLink.className = 'modal-download-btn';
                        downloadLink.target = '_blank'; // Open in new tab
                        modalDownloads.appendChild(downloadLink);
                    });
                }
                
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

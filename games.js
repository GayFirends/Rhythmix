document.addEventListener('DOMContentLoaded', () => {
    const games = [
        {
            id: 1,
            title: 'OSU!',
            genre: '音乐/PC',
            platform: 'pc',
            imageUrl: 'https://github.com/ppy/osu/raw/master/assets/lazer.png',
            description: 'PC端经典音游，内含Std,mania,taiko等模式'
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

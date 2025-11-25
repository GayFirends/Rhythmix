const { createApp, ref, onMounted } = Vue;

const app = createApp({
    setup() {
        // --- Data Refs ---
        const isLoading = ref(true);

        const features = ref([
            {
                icon: 'fas fa-bolt',
                title: '极速下载',
                description: '采用OneDrive网盘直连下载，与使用国内相关网盘不同，免登录，免VIP,可以直接使用IDM、NDM、FDM等多线程下载工具下载'
            },
            {
                icon: 'fas fa-game',
                title: '海量游戏库',
                description: '不断收录各类音游安装包，安卓用户提供APK等类型安装包，iOS/iPadOS提供官方APP Store链接。'
            },
            {
                icon: 'fas fa-shield-alt',
                title: '安全无毒',
                description: '所有资源均取自于官网、Google Play、App Store，保证资源无毒无害，放心游玩~'
            }
        ]);

        const news = ref([
            {
                id: 1,
                title: '网站 V2.0 全新上线！',
                summary: '我们很高兴地宣布，Rhythmix 网站已更新至全新版本，带来了更流畅的体验和更丰富的内容。',
                date: '2025年11月25日'
            },
            {
                id: 2,
                title: '“霓虹深渊” 曲包更新',
                summary: '热门游戏“霓虹深渊”现已加入包含 5 首新曲的扩展包，快来挑战吧！',
                date: '2025年11月22日'
            }
        ]);

        // --- Lifecycle Hooks ---
        onMounted(() => {
            // --- Preloader Logic ---
            // Simulate content loading
            setTimeout(() => {
                isLoading.value = false;
                const loader = document.getElementById('loader');
                const appElement = document.getElementById('app');
                if (loader) {
                    loader.style.opacity = '0';
                    // Remove loader from DOM after transition
                    setTimeout(() => loader.style.display = 'none', 500); 
                }
                if (appElement) {
                    appElement.classList.remove('hidden');
                    appElement.classList.add('visible');
                }
            }, 1000); // Simulate a 1-second load time

            // --- Scroll Animation Logic ---
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                    }
                });
            }, {
                threshold: 0.1 // Trigger when 10% of the element is visible
            });

            // Observe all elements with the .anim-on-scroll class
            document.querySelectorAll('.anim-on-scroll').forEach((el) => {
                observer.observe(el);
            });
        });

        // --- Return values to be used in the template ---
        return {
            isLoading,
            features,
            news
        };
    }
});

app.mount('#app');

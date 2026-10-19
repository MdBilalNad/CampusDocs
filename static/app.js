document.addEventListener('DOMContentLoaded', () => {
    // --- LIVE COUNT (Find Page) ---
    const filterForm = document.querySelector('form[action="/projects"]');
    const countDisplay = document.getElementById('live-count');

    if (filterForm && countDisplay) {
        const updateCount = async () => {
            const formData = new FormData(filterForm);
            const params = new URLSearchParams(formData);
            
            try {
                const res = await fetch(`/api/count?${params.toString()}`);
                const data = await res.json();
                
                // Premium micro-interaction: scale down, swap text, scale up
                countDisplay.style.transition = 'transform 0.15s ease, opacity 0.15s ease';
                countDisplay.style.transform = 'scale(0.9)';
                countDisplay.style.opacity = '0.5';
                
                setTimeout(() => {
                    countDisplay.innerText = data.count;
                    countDisplay.style.transform = 'scale(1)';
                    countDisplay.style.opacity = '1';
                }, 150);

            } catch (e) {
                console.error("Error fetching count", e);
            }
        };

        filterForm.querySelectorAll('input').forEach(el => {
            el.addEventListener('input', updateCount);
            el.addEventListener('change', updateCount);
        });
        
        updateCount();
    }

    // --- SIDE PANEL (Projects Page) ---
    const overlay = document.getElementById('overlay');
    const panel = document.getElementById('panel');
    const panelContent = document.getElementById('panel-content');
    const cards = document.querySelectorAll('.project-card');

    if (cards.length > 0 && overlay && panel) {
        cards.forEach(card => {
            card.addEventListener('click', async () => {
                const domainSlug = card.dataset.domain;
                const id = card.dataset.id;
                
                panelContent.innerHTML = '<p class="mono" style="color: var(--text-muted);">FETCHING DATA...</p>';
                overlay.classList.add('open');
                panel.classList.add('open');

                try {
                    const res = await fetch(`/api/project/${domainSlug}/${id}`);
                    const data = await res.json();
                    const p = data.project;
                    const stack = data.broad_tech_stack;

                    let broadStackHtml = '';
                    for (const [key, val] of Object.entries(stack)) {
                        if (val.length > 0) {
                            broadStackHtml += `
                            <div style="margin-bottom: 1rem;">
                                <div class="mono" style="color: var(--text-muted); margin-bottom: 0.2rem;">${key.replace('_', ' ')}</div>
                                <div style="font-size: 0.85rem; color: var(--text-main);">${val.join(', ')}</div>
                            </div>`;
                        }
                    }

                    panelContent.innerHTML = `
                        <div class="mono mb-4" style="color: var(--accent);">${p.domain}</div>
                        <h2 style="font-size: 2.5rem; margin-bottom: 1rem;">${p.title}</h2>
                        <div class="mono mb-4" style="display:flex; gap: 1rem; color: var(--text-muted);">
                            <span>${p.difficulty.toUpperCase()}</span>
                            <span>•</span>
                            <span>${p.estimated_time.toUpperCase()}</span>
                        </div>
                        <p style="color: var(--text-main); font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.6;">${p.description}</p>
                        
                        <div class="mono mb-4" style="color: var(--text-muted);">Project Stack</div>
                        <div class="tag-row mb-4">
                            ${p.tech_stack.map(t => `<span class="tag">${t}</span>`).join('')}
                        </div>

                        <div style="border-top: 1px solid var(--border); margin-top: 2rem; padding-top: 2rem;">
                            <div class="mono mb-4" style="color: var(--text-muted);">Domain Context</div>
                            ${broadStackHtml}
                        </div>
                    `;
                    
                    // Fade in the loaded content
                    panelContent.style.opacity = '0';
                    panelContent.style.transition = 'opacity 0.3s';
                    setTimeout(() => { panelContent.style.opacity = '1'; }, 50);

                } catch (e) {
                    panelContent.innerHTML = '<p style="color: red;">Error loading project.</p>';
                }
            });
        });

        const closePanel = () => {
            overlay.classList.remove('open');
            panel.classList.remove('open');
            // Clear content after transition ends to prevent ghosting
            setTimeout(() => { panelContent.innerHTML = ''; }, 400);
        };

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closePanel();
        });
        
        overlay.addEventListener('click', closePanel);
    }
});
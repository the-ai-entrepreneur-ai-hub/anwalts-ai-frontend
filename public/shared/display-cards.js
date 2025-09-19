/**
 * DisplayCards - Vanilla JS implementation of stacked card component
 */
(function() {
  'use strict';

  // Default Sparkles icon as SVG
  const SPARKLES_ICON = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.582a.5.5 0 0 1 0 .962L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>`;

  function createDisplayCard(config) {
    const {
      className = '',
      icon = SPARKLES_ICON,
      title = 'Featured',
      description = 'Discover amazing content',
      date = 'Just now',
      titleClassName = ''
    } = config;

    const card = document.createElement('div');
    card.className = `display-card ${className}`;
    
    card.innerHTML = `
      <div class="dc-head">
        <span class="dc-icon">${icon}</span>
        <p class="dc-title ${titleClassName}">${title}</p>
      </div>
      <p class="dc-desc">${description}</p>
      <p class="dc-date">${date}</p>
    `;

    return card;
  }

  function createDisplayCards(cards = null) {
    const container = document.createElement('div');
    container.className = 'display-cards-container';

    // Default cards if none provided
    const defaultCards = [
      { 
        className: 'dc-1',
        title: 'Featured',
        description: 'Discover amazing content',
        date: 'Just now'
      },
      { 
        className: 'dc-2',
        title: 'Popular',
        description: 'Trending right now',
        date: '2 hours ago'
      },
      { 
        className: 'dc-3',
        title: 'Latest',
        description: 'Fresh updates available',
        date: '1 day ago'
      }
    ];

    const cardsToRender = cards && cards.length ? cards : defaultCards;
    
    // Add data attribute for progress indicator
    container.setAttribute('data-cards', cardsToRender.length);
    
    cardsToRender.forEach(cardConfig => {
      const card = createDisplayCard(cardConfig);
      container.appendChild(card);
    });

    return container;
  }

  function createDisplayCardGroups(groups = []) {
    const wrapper = document.createElement('div');
    wrapper.className = 'display-card-groups-wrapper';
    wrapper.style.cssText = 'display: flex; flex-direction: column; gap: 40px; width: 100%;';

    groups.forEach(cards => {
      const groupContainer = document.createElement('div');
      groupContainer.style.cssText = 'display: flex; width: 100%; justify-content: center;';
      
      const displayCards = createDisplayCards(cards);
      groupContainer.appendChild(displayCards);
      wrapper.appendChild(groupContainer);
    });

    return wrapper;
  }

  // Enhanced animation controller
  function initCardAnimations(container) {
    const cards = container.querySelectorAll('.display-card');
    if (cards.length < 2) return;

    let currentIndex = 0;
    let isHovered = false;
    
    // Add hover listeners
    container.addEventListener('mouseenter', () => {
      isHovered = true;
    });
    
    container.addEventListener('mouseleave', () => {
      isHovered = false;
    });

    // Add click listeners for manual navigation
    cards.forEach((card, index) => {
      card.addEventListener('click', () => {
        if (!isHovered) return;
        currentIndex = index;
        updateActiveCard();
      });
    });

    function updateActiveCard() {
      cards.forEach((card, index) => {
        card.classList.toggle('dc-active', index === currentIndex);
      });
    }

    // Auto-advance every 4 seconds when not hovered
    setInterval(() => {
      if (!isHovered) {
        currentIndex = (currentIndex + 1) % cards.length;
        updateActiveCard();
      }
    }, 4000);

    // Initialize first card as active
    updateActiveCard();
  }

  // Auto-initialize any containers with data attributes
  document.addEventListener('DOMContentLoaded', function() {
    // Find containers with data-display-cards attribute
    const containers = document.querySelectorAll('[data-display-cards]');
    
    containers.forEach(container => {
      try {
        const configStr = container.getAttribute('data-display-cards');
        const config = configStr ? JSON.parse(configStr) : null;
        
        if (config && config.groups) {
          // Multiple groups
          const groupsElement = createDisplayCardGroups(config.groups);
          container.appendChild(groupsElement);
          
          // Initialize animations for each group
          const cardContainers = groupsElement.querySelectorAll('.display-cards-container');
          cardContainers.forEach(initCardAnimations);
        } else if (config && config.cards) {
          // Single group
          const cardsElement = createDisplayCards(config.cards);
          container.appendChild(cardsElement);
          initCardAnimations(cardsElement);
        } else {
          // Default cards
          const cardsElement = createDisplayCards();
          container.appendChild(cardsElement);
          initCardAnimations(cardsElement);
        }
      } catch (e) {
        console.warn('Failed to initialize DisplayCards:', e);
        // Fallback to default
        const cardsElement = createDisplayCards();
        container.appendChild(cardsElement);
        initCardAnimations(cardsElement);
      }
    });
  });

  // Export for manual use
  window.DisplayCards = {
    create: createDisplayCards,
    createGroups: createDisplayCardGroups,
    createCard: createDisplayCard
  };
})();
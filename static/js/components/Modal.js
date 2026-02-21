export class Modal {
    constructor(modalId) {
        this.modalEl = document.getElementById(modalId);
        this.overlayEl = document.getElementById('m-overlay');
        this.titleEl = document.getElementById('m-t');
        this.noteEl = document.getElementById('m-n');
        this.closeBtn = document.getElementById('m-close');

        this.bindEvents();
    }

    bindEvents() {
        this.overlayEl.addEventListener('click', () => {
            this.close();
        });

        this.closeBtn.addEventListener('click', () => {
            this.close();
        });
    }

    show(time, stars, noteText) {
        this.titleEl.textContent = time + stars;
        this.noteEl.textContent = noteText;
        this.modalEl.classList.add('show');
    }

    close() {
        this.modalEl.classList.remove('show');
    }
}

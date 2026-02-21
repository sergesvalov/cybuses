export class Modal {
    constructor(modalId) {
        this.modalEl = document.getElementById(modalId);
        this.titleEl = document.getElementById('m-t');
        this.noteEl = document.getElementById('m-n');
        this.closeBtn = document.getElementById('m-close');

        this.bindEvents();
    }

    bindEvents() {
        this.modalEl.addEventListener('click', (e) => {
            if (e.target === this.modalEl) {
                this.close();
            }
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

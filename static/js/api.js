export class Api {
    /**
     * @returns {Promise<Array>} Routes data
     */
    static async fetchData() {
        const res = await fetch('/api/data');
        return await res.json();
    }

    /**
     * Triggers backend cache refresh and polls until task is finished
     */
    static async refreshData() {
        await fetch('/api/refresh', { method: 'POST' });

        return new Promise((resolve) => {
            const iv = setInterval(async () => {
                const res = await fetch('/api/status');
                const s = await res.json();

                if (!s.updating) {
                    clearInterval(iv);
                    resolve();
                }
            }, 2000);
        });
    }
}

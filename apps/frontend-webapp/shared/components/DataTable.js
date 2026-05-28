/**
 * Shared data table renderer.
 */

(function initDataTable() {
    class DataTable {
        constructor(containerOrElement, options) {
            // Handle string ID or DOM element
            if (typeof containerOrElement === 'string') {
                this.tableBody = document.getElementById(containerOrElement);
            } else {
                this.tableBody = containerOrElement;
            }
            
            // Handle new object format or legacy array format
            if (Array.isArray(options)) {
                this.columns = options;
                this.rowClassName = null;
                this.rowDataset = null;
            } else {
                this.columns = options.columns || [];
                this.rowClassName = options.rowClassName || null;
                this.rowDataset = options.rowDataset || null;
            }
        }

        render(items) {
            this.tableBody.innerHTML = items.map(item => {
                const rowClass = this.rowClassName ? this.rowClassName(item) : '';
                const rowDataset = this.rowDataset ? this.rowDataset(item) : {};
                const dataAttrs = Object.entries(rowDataset).map(([k, v]) => `data-${k}="${v}"`).join(' ');
                
                return `
                    <tr class="${rowClass}" ${dataAttrs}>
                        ${this.columns.map(column => `<td class="${column.className || ''}">${column.render(item)}</td>`).join('')}
                    </tr>
                `;
            }).join('');
        }

        renderEmpty(message, colspan) {
            this.tableBody.innerHTML = `<tr><td colspan="${colspan || this.columns.length}" class="text-center">${message}</td></tr>`;
        }
    }

    window.grindx = window.grindx || {};
    window.grindx.components = {
        ...(window.grindx.components || {}),
        DataTable
    };
})();

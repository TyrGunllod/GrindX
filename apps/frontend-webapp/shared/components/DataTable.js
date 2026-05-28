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
                const expandIcon = this.rowClassName ? '<i class="fas fa-chevron-right expand-icon"></i>' : '';
                
                return `
                    <tr class="${rowClass}" ${dataAttrs}>
                        ${expandIcon ? `<td style="width: 30px; text-align: center;">${expandIcon}</td>` : ''}
                        ${this.columns.map(column => {
                            const value = column.key ? item[column.key] : '';
                            const content = column.render ? column.render(value, item) : value;
                            return `<td class="${column.className || ''}">${content}</td>`;
                        }).join('')}
                    </tr>
                `;
            }).join('');
        }

        renderEmpty(message, colspan) {
            const totalCols = this.rowClassName ? this.columns.length + 1 : this.columns.length;
            this.tableBody.innerHTML = `<tr><td colspan="${colspan || totalCols}" class="text-center">${message}</td></tr>`;
        }
    }

    window.grindx = window.grindx || {};
    window.grindx.components = {
        ...(window.grindx.components || {}),
        DataTable
    };
})();

/**
 * Shared data table renderer.
 */

(function initDataTable() {
    class DataTable {
        constructor(tableBody, columns) {
            this.tableBody = tableBody;
            this.columns = columns;
        }

        render(items) {
            this.tableBody.innerHTML = items.map(item => `
                <tr>
                    ${this.columns.map(column => `<td class="${column.className || ''}">${column.render(item)}</td>`).join('')}
                </tr>
            `).join('');
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

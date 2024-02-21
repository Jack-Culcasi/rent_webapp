$(document).ready(function() {
  $('.sort-link').click(function(e) {
      e.preventDefault();
      const sortBy = $(this).data('sort');
      const tableId = $(this).closest('table').attr('id');
      const sortOrder = $(this).data('sort-order') || 'asc'; // Default to ascending order if not previously set
      const newSortOrder = sortOrder === 'asc' ? 'desc' : 'asc'; // Toggle sorting order

      sortTable(tableId, sortBy, newSortOrder);
      
      // Update data-sort-order attribute to reflect the new sorting order
      $(this).data('sort-order', newSortOrder);
  });

  function sortTable(tableId, sortBy, sortOrder) {
      const rows = $(`#${tableId} tbody tr`).get();

      rows.sort(function(rowA, rowB) {
          let valueA = $(rowA).find(`td[data-sort="${sortBy}"]`).text().toUpperCase();
          let valueB = $(rowB).find(`td[data-sort="${sortBy}"]`).text().toUpperCase();

          // Toggle sorting order based on sortOrder
          if (sortOrder === 'desc') {
              [valueA, valueB] = [valueB, valueA]; // Swap values for descending order
          }

          return valueA.localeCompare(valueB);
      });

      $(`#${tableId} tbody`).empty().append(rows);
  }
});

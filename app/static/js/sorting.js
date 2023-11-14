$(document).ready(function() {
    $('.sort-link').click(function(e) {
      e.preventDefault();
      const sortBy = $(this).data('sort');
      sortTable(sortBy);
    });
  
    function sortTable(sortBy) {
      const rows = $('#carTable tbody tr').get();
  
      rows.sort(function(rowA, rowB) {
        const valueA = $(rowA).find(`td[data-sort="${sortBy}"]`).text().toUpperCase();
        const valueB = $(rowB).find(`td[data-sort="${sortBy}"]`).text().toUpperCase();
  
        return valueA.localeCompare(valueB);
      });
  
      $('#carTable tbody').empty().append(rows);
    }
  });
  
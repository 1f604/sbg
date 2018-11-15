// Fuck yeah, regular expressions! regex ftw!
function searchTable(col, fieldname) {
    let tabel, filter, input, tr, td, i;
    input = document.getElementById(fieldname); //"tags-search"
    filter = input.value.toUpperCase();
    tabel = document.getElementById("myTable");
    tr = document.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
        if (tr[i].cells[col].textContent.trim().toUpperCase().match(filter) !== null) {
            tr[i].style.display = "";
        } else {
            tr[i].style.display = "none";
        }
    }
}

// Using mergesort because chrome's built in sort is unstable. 
function mergeSort (arr, func) {
  if (arr.length === 1) {
    // return once we hit an array with a single item
    return arr
  }

  const middle = Math.floor(arr.length / 2) // get the middle item of the array rounded down
  const left = arr.slice(0, middle) // items on the left side
  const right = arr.slice(middle) // items on the right side

  return merge(
    mergeSort(left, func),
    mergeSort(right, func), func
  )
}

// compare the arrays item by item and return the concatenated result
function merge (left, right, func) {
  let result = []
  let indexLeft = 0
  let indexRight = 0

  while (indexLeft < left.length && indexRight < right.length) {
    if (func(left[indexLeft], right[indexRight]) < 1) {
      result.push(left[indexLeft])
      indexLeft++
    } else {
      result.push(right[indexRight])
      indexRight++
    }
  }
  return result.concat(left.slice(indexLeft)).concat(right.slice(indexRight))
}

function sortTable(table, col, reverse) {
    let tb = table.tBodies[0]; // use `<tbody>` to ignore `<thead>` and `<tfoot>` rows
    let tr = Array.prototype.slice.call(tb.rows, 0); // put rows into array
    let i;
    reverse = -((+reverse) || -1);
    let classname = tr[0].cells[col].className;
    let compare = function (classname, a,b) {
        if (classname === 'posted' || classname == 'updated'){
            return Date.parse(a) - Date.parse(b);
        }
        if (classname === 'length'){
            return parseInt(a) - parseInt(b);
        }
        else{
            return a.localeCompare(b);
        }
    };
    tr = mergeSort(tr, function (a, b) { // sort rows
        return reverse // `-1 *` if want opposite order
            * compare(classname, a.cells[col].textContent.trim(), b.cells[col].textContent.trim());
    });
    for(i = 0; i < tr.length; ++i) tb.appendChild(tr[i]); // append each row in order
}

function makeSortable(table) {
    let th = table.tHead, i;
    th && (th = th.rows[0]) && (th = th.cells);
    if (th) i = th.length;
    else return; // if no `<thead>` then do nothing
    while (--i >= 0) (function (i) {
        let dir = 1;
        th[i].addEventListener('click', function () {sortTable(table, i, (dir = 1 - dir))});
    }(i));
}

function makeAllSortable(parent) {
    parent = parent || document.body;
    let t = parent.getElementsByTagName('table'), i = t.length;
    while (--i >= 0) makeSortable(t[i]);
}

window.onload = function () {
    makeAllSortable();
    sortTable(document.getElementById("entries"), 0, -1);
};

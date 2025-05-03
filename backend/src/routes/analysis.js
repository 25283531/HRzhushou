const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({
    success: true,
    data: {
      tableData: [],
      tableColumns: [],
      chartData: {}
    }
  });
});

module.exports = router; 
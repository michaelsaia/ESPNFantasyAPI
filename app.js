const express = require('express');
const {spawn} = require('child_process');
app = express();

app.use(express.static('public'));
//app.use(bodyParser.urlencoded({extended:true}));

const path = require('path');
const scriptLoc = path.join(__dirname, "public", "python", "dataScraping.py");
const driveLoc = path.join(__dirname, "public", "python","chromedriver_win32" ,"chromedriver.exe");

app.get('/:format/:numPlayers', (req, res) => {
  // spawn new child process to call the python script
 const python = spawn('python', [scriptLoc, req.params.format, req.params.numPlayers, driveLoc]);
 // collect data from script
 var dataToSend;
 python.stdout.on('data', function (data) {
   console.log('Pipe data from python script ...');
   dataToSend = data.toString();
 });

 python.stderr.on('data', data => {
   console.error(`stderr: ${data}`)
 })

 python.on('close', (code) => {
   console.log(`child process close all stdio with code ${code}`);
   // send data to browser
   res.send(dataToSend)
  });
});




app.listen(process.env.PORT || 3000, function () {
  console.log('Server has started');
});

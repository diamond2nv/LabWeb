//diamond2nv @ github.com
var mosca = require('mosca');

module.exports = {
  port: 1883,
  // host: "127.0.0.1", // specify an host to bind to a single interface
  id: 'mymosca', // used to publish in the $SYS/<id> topicspace
  stats: true, // publish stats in the $SYS/<id> topicspace
  logger: {
    level: 'info'
  },
  backend: {
    type: 'redis',
    port: 6363,
    host: 'localhost',
    return_buffers: true
  },
  persistence: {
    factory: mosca.persistence.Redis,
    port: 6363,
    host: 'localhost'
  }
};
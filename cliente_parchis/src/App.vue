<template>
  <div id="app">
    <input v-model="message" @keyup.enter="sendMessage" placeholder="Type a message" />
    <label for="message">Message {{ cliente }}</label>
    <button @click="solicitudColor">Send</button>
    <ul>
      <li v-for="(msg, index) in messages" :key="index">{{ msg }}</li>
    </ul>
  </div>
</template>

<script>
import websocket from "vue-native-websocket";
export default {
  data() {
    return {
      message: "",
      messages: [],
    };
  },
  mounted() {
    // Variable para definir si se juega en local
    const local = false;

    // Cambio de IPs 
    let IP_SERVER_PUBLICA;
    if (local) {
      // IP servidor local
      IP_SERVER_PUBLICA = "localhost";
    } else {
      // IP servidor público
      IP_SERVER_PUBLICA = "192.168.20.12";
    }

    // Puerto del servidor
    const PORT_SERVER = 8001;

    // Conectarse al servidor
    const cliente = new WebSocket(`ws://${IP_SERVER_PUBLICA}:${PORT_SERVER}`);

    // Evento cuando la conexión se abre
    cliente.addEventListener('open', (event) => {
    console.log('Conexión establecida con el servidor', event);
    // Aquí puedes realizar acciones adicionales después de establecer la conexión
});

// Evento cuando se recibe un mensaje del servidor
cliente.addEventListener('message', (event) => {
  const mensaje = JSON.parse(event.data);
  console.log('Mensaje recibido:', mensaje);
  // Aquí puedes realizar acciones adicionales al recibir un mensaje del servidor
});

// Evento cuando se produce un error en la conexión
cliente.addEventListener('error', (event) => {
  console.error('Error en la conexión:', event);
  // Aquí puedes realizar acciones adicionales al producirse un error
});

// Evento cuando la conexión se cierra
cliente.addEventListener('close', (event) => {
  console.log('Conexión cerrada:', event);
  // Aquí puedes realizar acciones adicionales al cerrar la conexión
});

  },
  methods: {
    sendMessage() {
      if (this.message.trim() !== "") {
        console.log("Sending message: ", this.message);
        this.$socket.send(this.message);
        this.message = "";
      }
    },
    solicitudColor() {
      const solicitud = { tipo: "solicitud_color" };
      // Convierte el objeto a una cadena JSON y la envía al servidor
      websocket.send(JSON.stringify(solicitud));
    },
  },
};
</script>

<style>
#app {
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

ul {
  list-style-type: none;
  padding: 0;
}
</style>

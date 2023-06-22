import { ChakraProvider, Flex } from "@chakra-ui/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { render } from 'react-dom';

import EventViewer from "./components/EventViewer";
import Header from "./components/Header";
import StatusMonitor from "./components/StatusMonitor";
import './index.css';

// const END_POINT = "http://localhost:8000"
const END_POINT = '';
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
    <ChakraProvider>
      <Flex height="100%" flexDir="column">
      <Header />
      <StatusMonitor url={END_POINT}/>
      <EventViewer url={END_POINT}/>
      </Flex>
    </ChakraProvider>
    </QueryClientProvider>
  )
}

const rootElement = document.getElementById("root");
render(<App />, rootElement);
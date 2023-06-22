import { ArrowForwardIcon, RepeatIcon } from "@chakra-ui/icons";
import { Badge, Box, Divider, Flex, IconButton, Spinner, Tag, Text } from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import React, {Label} from "react";
import NetworkInfo from "./Network";

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}

const Link = ({url, link}) => {
    const queryClient = useQueryClient();
    const queryKey = ["link", link.src, link.dst];
    const statusQuery = useQuery(queryKey, async () => {
        const res = await fetch(url+"/links/"+link["src"]+"/"+link["dst"]);
        return await res.json();
    }, {
        staleTime: 10000,
        cacheTime: 5000,
        refetchInterval: 10000,
    });

    if (!statusQuery.isFetched) {
        return (<p>Loading</p>)
    }

    const status = statusQuery.data;
    const updateStatus = (event: Event) => {
        queryClient.invalidateQueries(queryKey)
    }

    const seqDiff = ({tx_seq, rx_seq}) => {
        if (tx_seq > rx_seq) {
            return <span size='xs'>&nbsp;(-{tx_seq - rx_seq})</span>;
        } else {
            return null;
        }
    }

    return (
        <Box p="2" borderColor="gray.400" borderWidth="1px" borderRadius="lg" margin="2px" width="50%" id="network-info">
        <Flex>
            <Flex flex="1">
            <NetworkInfo url={url} id={status.src} name={status.src_name} />
            &nbsp;
            <ArrowForwardIcon margin="0.3" />
            &nbsp;
            <NetworkInfo url={url} id={status.dst} name={status.dst_name} />
            </Flex>
            {status.tx_seq > status.rx_seq && <Flex>Delivering<IconButton size="xs" margin="2px" isLoading="true" /></Flex>}
            <IconButton margin="2px" size="xs" onClick={updateStatus} isLoading={statusQuery.isLoading} icon={<RepeatIcon />} />
        </Flex>
        <Divider />
        <Flex id="network-description">
        <Flex fontSize="sm">TX &bull; {status.tx_seq}</Flex>
        <Flex fontSize="sm">RX &bull; {status.rx_seq}{seqDiff(status)}</Flex>
        <Flex fontSize="sm">TXH &bull; {status.tx_height}</Flex>
        <Flex fontSize="sm">RXH &bull; {status.rx_height}</Flex>
        <Flex fontSize="sm">PENDING &bull; {status.pending_count}</Flex>
        <Flex fontSize="sm">DELAY &bull; {status.pending_delay}</Flex>
        </Flex>
        <Divider />
        <Flex id="network-state">
        <Badge flex="1" textAlign="center" fontSize="lg" colorScheme={COLOR_FOR[status.state]}>{String(status.state).toUpperCase()}</Badge>
        </Flex>
        </Box>
    );
}

export default Link;
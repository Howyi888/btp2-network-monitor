import { ArrowForwardIcon, RepeatIcon } from "@chakra-ui/icons";
import { Badge, Box, Divider, Flex, HStack, IconButton, Tooltip } from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import React from "react";
import { strfdelta } from "../utils";
import NetworkInfo from "./Network";

const COLOR_FOR = {
    good: 'green',
    bad: 'red'
}

const LinkDescItem = ({title, desc, value}) => {
    return (
        <Flex fontSize="sm">
            <Flex flex="1" justifyContent="right">
            <Tooltip label={desc || ""}>{title}</Tooltip>
            &nbsp;&bull;&nbsp;
            </Flex>
            <Flex flex="1">
             {value}
            </Flex>
        </Flex>
    )
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
        queryClient.invalidateQueries(queryKey);
    }

    return (
        <Box p="2" className="link-info">
        <Flex className="link-header">
            <HStack flex="1" overflowX="hidden" mr="10px">
            <NetworkInfo url={url} id={status.src} name={status.src_name} />
            &nbsp;
            <ArrowForwardIcon />
            &nbsp;
            <NetworkInfo url={url} id={status.dst} name={status.dst_name} />
            </HStack>
            {status.tx_seq > status.rx_seq && <Flex className="delivering">Delivering<IconButton size="xs" margin="2px" isLoading="true" /></Flex>}
            <IconButton margin="2px" size="xs" onClick={updateStatus} isLoading={statusQuery.isLoading} icon={<RepeatIcon />} />
        </Flex>
        <Divider />
        <Flex className="link-description">
        <LinkDescItem title="TX Sequence" value={status.tx_seq} />
        <LinkDescItem title="RX Sequence" value={status.rx_seq} />
        <LinkDescItem title="TX Height" desc='Last block height of source blockchain' value={status.tx_height} />
        <LinkDescItem title="RX Height" desc='Last block height of BMV in target blockchain' value={status.rx_height} />
        <LinkDescItem title="Pending Count" desc='Pending message count' value={status.pending_count} />
        <LinkDescItem title="Pending Delay" desc='Delay after first pending message' value={strfdelta(status.pending_delay)} />
        </Flex>
        <Divider />
        <Flex className="network-state">
        <Badge flex="1" textAlign="center" fontSize="lg" colorScheme={COLOR_FOR[status.state]}>{String(status.state).toUpperCase()}</Badge>
        </Flex>
        </Box>
    );
}

export default Link;
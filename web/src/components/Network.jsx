import {
    Heading,
    Popover, PopoverArrow, PopoverBody,
    PopoverCloseButton,
    PopoverContent,
    PopoverHeader, PopoverTrigger,
    Table, Tbody, Td, Th,
    Tr
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import React, { useRef } from "react";

const NetworkInfo = ({url, id, name}) =>  {
    const infoQuery = useQuery( ["networkInfo", id], async () => {
            const res = await fetch(url+"/network/"+id)
            const jso = await res.json();
            return jso;
        },
        {
            staleTime: Infinity,
            cacheTime: Infinity,
        },
    );
    const makeInfoContent = (info: any) => {
        return (
            <Table size="sm">
                <Tbody>
                    <Tr><Th>Type</Th><Td>{info.type}</Td></Tr>
                    <Tr><Th>Network</Th><Td>{info.network}</Td></Tr>
                    { info.name && <Tr><Th>Name</Th><Td>{info.name}</Td></Tr> }
                    { info.endpoint && <Tr><Th>EndPoint</Th><Td>{info.endpoint}</Td></Tr> }
                    { info.tx_limit && <Tr><Th>TxLimit</Th><Td isNumeric>{info.tx_limit} seconds</Td></Tr> }
                    { info.rx_limit && <Tr><Th>RxLimit</Th><Td isNumeric>{info.rx_limit} seconds</Td></Tr> }
                    { info.bmc && <Tr><Th>BMC</Th><Td>{info.bmc}</Td></Tr> }
                    { info.bmcm && <Tr><Th>BMCM</Th><Td>{info.bmcm}</Td></Tr> }
                    { info.bmcs && <Tr><Th>BMCS</Th><Td>{info.bmcs}</Td></Tr> }
                </Tbody>
            </Table>
        )
    };
    const initialFocus = useRef();

    return (
        <Popover isLazy="true" preventOverflow="true" boundary="scrollParent"
            initialFocusRef={initialFocus} id="network-name">
            <PopoverTrigger><Heading size="sm">{name}</Heading></PopoverTrigger>
            <PopoverContent width="auto" id='network-info' borderColor="gray.400" marginLeft="6px">
                <PopoverArrow bg="gray.300" />
                <PopoverCloseButton ref={initialFocus} />
                <PopoverHeader bg="gray.200">
                    <Heading size="sm">{name}</Heading>
                </PopoverHeader>
                <PopoverBody>
                    {infoQuery.isLoading ? <Heading>Loading</Heading> : makeInfoContent(infoQuery.data)}
                </PopoverBody>
            </PopoverContent>
        </Popover>
    )
};

export default NetworkInfo;
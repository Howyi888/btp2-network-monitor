import { Table, Tbody, Td, Th, Tr } from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";

function toN(s: string): string {
    let items = [];
    const mod = s.length % 3
    if (mod > 0) {
        items.push(s.slice(0,mod));
        s = s.slice(mod);
    }
    while (s.length>0) {
        items.push(s.slice(0,3));
        s = s.slice(3);
    }
    return items.map((item, idx)=>{return <span key={idx}>{item}</span>})
}

function formatFee(fee: int, decimal: int): string {
    let vs = String(fee);
    if (vs.length < decimal) {
        vs = '0'.repeat(decimal-vs.length) + vs;
    }
    let high, low;
    if (vs.length === decimal) {
        low = vs
        high = '0'
    }  else {
        const sep = vs.length-decimal;
        high = vs.slice(0,sep);
        low = vs.slice(sep);
    }
    return (
        <>
            <span>{toN(high)}</span>.<span>{toN(low)}</span>
        </>
    )
}

const FeeEntry = ({table, entry}) => {
    return (
        <>
        <Tr>
            <Th rowSpan={2}>{entry['name']}</Th>
            <Th>1-way</Th>
            <Td>
            <span className="value">{formatFee(entry['fees'][0], table['decimal'])}</span>
            &nbsp;
            <span className="symbol">{table['symbol']}</span></Td>
        </Tr>
        <Tr>
            <Th>2-way</Th>
            <Td>
            <span className="value">{formatFee(entry['fees'][1], table['decimal'])}</span>
            &nbsp;
            <span className="symbol">{table['symbol']}</span>
            </Td>
        </Tr>
        </>
    )
};

const FeeTable = ({url, id}) => {
    const feeQuery = useQuery(["feetable", id], async () => {
        const res = await fetch(url+"/network/"+id+"/feetable")
        return await res.json();
    }, {
        staleTime: 10000,
        cacheTime: 10000,
    });

    const feeTable = feeQuery.data || { table: [] };

    return (
        <Table size="sm" className='fee-table'>
            <Tbody>
            { feeQuery.isLoading ? <Tr><Td>Loading</Td></Tr>
                : feeTable['table'].map((entry) => {
                    return <FeeEntry key={entry["id"]} entry={entry} table={feeTable} />
                })
            }
            </Tbody>
        </Table>
    )
}

export default FeeTable;